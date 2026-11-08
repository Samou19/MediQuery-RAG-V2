import logging
from time import perf_counter

from app.core.config import get_settings
from app.services.context_builder import build_context
from app.services.fusion import reciprocal_rank_fusion
from app.services.generation import generate_answer
from app.services.prompt_builder import build_prompt
from app.services.reranking import rerank_results
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever

logger = logging.getLogger(__name__)


def rag_query(question: str) -> dict:
    """
    Exécute le pipeline RAG complet de MediQuery V2
    et mesure le temps d'exécution de chaque composant.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    total_start = perf_counter()

    question = question.strip()
    settings = get_settings()

    timings = {}

    logger.info("Démarrage du pipeline RAG.")

    # --------------------------------------------------
    # 1. Recherche dense
    # --------------------------------------------------
    start = perf_counter()

    dense_results = dense_search(question=question, top_k=settings.TOP_K_DENSE)

    timings["dense_search"] = round((perf_counter() - start) * 1000, 2)

    # --------------------------------------------------
    # 2. Recherche sparse (BM25)
    # --------------------------------------------------
    start = perf_counter()

    sparse_retriever = SparseRetriever()

    try:
        sparse_retriever.build_index()

        timings["sparse_index_build"] = round((perf_counter() - start) * 1000, 2)

        start = perf_counter()

        sparse_results = sparse_retriever.search(
            question=question, top_k=settings.TOP_K_SPARSE
        )

        timings["sparse_search"] = round((perf_counter() - start) * 1000, 2)

    finally:
        sparse_retriever.close()

    # --------------------------------------------------
    # 3. Fusion RRF
    # --------------------------------------------------
    start = perf_counter()

    fused_results = reciprocal_rank_fusion(
        dense_results=dense_results,
        sparse_results=sparse_results,
        k=60,
        top_k=max(settings.TOP_K_DENSE, settings.TOP_K_SPARSE),
    )

    timings["rrf_fusion"] = round((perf_counter() - start) * 1000, 2)

    if not fused_results:
        raise RuntimeError("Aucun résultat trouvé par les systèmes de recherche.")

    # --------------------------------------------------
    # 4. Reranking
    # --------------------------------------------------
    start = perf_counter()

    reranked_results = rerank_results(
        question=question, candidates=fused_results, top_k=settings.TOP_K_RERANK
    )

    timings["reranking"] = round((perf_counter() - start) * 1000, 2)

    if not reranked_results:
        raise RuntimeError("Le reranking n'a retourné aucun résultat.")

    # --------------------------------------------------
    # 5. Construction du contexte
    # --------------------------------------------------
    start = perf_counter()

    context_data = build_context(
        candidates=reranked_results, max_chunks=settings.TOP_K_RERANK
    )

    timings["context_builder"] = round((perf_counter() - start) * 1000, 2)

    if not context_data["context"]:
        raise RuntimeError("Impossible de construire un contexte exploitable.")

    # --------------------------------------------------
    # 6. Construction du prompt
    # --------------------------------------------------
    start = perf_counter()

    messages = build_prompt(question=question, context_data=context_data)

    timings["prompt_builder"] = round((perf_counter() - start) * 1000, 2)

    # --------------------------------------------------
    # 7. Génération Claude
    # --------------------------------------------------
    start = perf_counter()

    generation_result = generate_answer(messages)

    timings["generation"] = round((perf_counter() - start) * 1000, 2)

    # --------------------------------------------------
    # 8. Temps total
    # --------------------------------------------------
    timings["total"] = round((perf_counter() - total_start) * 1000, 2)

    logger.info("Temps d'exécution du pipeline RAG : %s", timings)

    logger.info("Pipeline RAG terminé avec succès.")

    return {
        "question": question,
        "answer": generation_result["answer"],
        "sources": context_data["sources"],
        "chunks_used": context_data["chunks_used"],
        "model": generation_result["model"],
        "usage": generation_result["usage"],
        "timings_ms": timings,
    }

import logging

import voyageai

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def rerank_results(
    question: str, candidates: list[dict], top_k: int | None = None
) -> list[dict]:
    """
    Réordonne les candidats RRF avec Voyage AI Reranker.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    if not candidates:
        return []

    settings = get_settings()

    if top_k is None:
        top_k = settings.TOP_K_RERANK

    if top_k <= 0:
        raise ValueError("top_k doit être positif.")

    # Textes à évaluer
    documents = [candidate["text"] for candidate in candidates]

    # Initialisation du client Voyage AI
    client = voyageai.Client(api_key=settings.VOYAGE_API_KEY)

    # Appel du modèle de reranking
    response = client.rerank(
        query=question,
        documents=documents,
        model=settings.VOYAGE_RERANK_MODEL,
        top_k=min(top_k, len(documents)),
        truncation=False,
    )

    # Reconstruction des résultats avec les scores
    reranked_results = []

    for rank, result in enumerate(response.results, start=1):
        candidate = candidates[result.index].copy()

        candidate["rerank_score"] = result.relevance_score
        candidate["rerank_rank"] = rank

        reranked_results.append(candidate)

    logger.info(
        "Reranking terminé : %s candidats analysés, %s conservés.",
        len(candidates),
        len(reranked_results),
    )

    return reranked_results

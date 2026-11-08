from app.services.context_builder import build_context
from app.services.fusion import reciprocal_rank_fusion
from app.services.generation import generate_answer
from app.services.prompt_builder import build_prompt
from app.services.reranking import rerank_results
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever

question = (
    "Quelles sont les étapes du parcours de soins "
    "d'un patient adulte vivant avec un diabète de type 2 ?"
)

sparse_retriever = SparseRetriever()

try:
    # 1. Retrieval Dense
    dense_results = dense_search(question, top_k=10)

    # 2. Retrieval Sparse
    sparse_retriever.build_index()

    sparse_results = sparse_retriever.search(question, top_k=10)

    # 3. Fusion RRF
    fused_results = reciprocal_rank_fusion(
        dense_results=dense_results, sparse_results=sparse_results, k=60, top_k=10
    )

    # 4. Reranking
    reranked_results = rerank_results(
        question=question, candidates=fused_results, top_k=5
    )

    # 5. Construction du contexte
    context_data = build_context(candidates=reranked_results)

    # 6. Construction du prompt
    messages = build_prompt(question=question, context_data=context_data)

    # 7. Génération avec Claude
    result = generate_answer(messages)

    print("\n" + "=" * 70)
    print("RÉPONSE MEDIQUERY")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("MÉTADONNÉES DE GÉNÉRATION")
    print("=" * 70)

    print("Modèle :", result["model"])
    print("Utilisation :", result["usage"])

finally:
    sparse_retriever.close()

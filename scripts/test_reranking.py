from app.services.context_builder import build_context
from app.services.fusion import reciprocal_rank_fusion
from app.services.reranking import rerank_results
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever

question = (
    "Quelles sont les étapes du parcours de soins "
    "d'un patient adulte vivant avec un diabète de type 2 ?"
)

# 1. Dense retrieval
dense_results = dense_search(question, top_k=10)

# 2. Sparse retrieval
sparse_retriever = SparseRetriever()

try:
    sparse_retriever.build_index()
    sparse_results = sparse_retriever.search(question, top_k=10)
finally:
    sparse_retriever.close()

# 3. Fusion RRF
fused_results = reciprocal_rank_fusion(
    dense_results=dense_results, sparse_results=sparse_results, k=60, top_k=10
)

# 4. Reranking
reranked_results = rerank_results(question=question, candidates=fused_results, top_k=5)

# 5. Affichage
print("\n========== RÉSULTATS RERANKING ==========\n")

for result in reranked_results:
    print(f"Rang final : {result['rerank_rank']}")
    print(f"ID : {result['id']}")
    print(f"Score RRF : {result['rrf_score']:.6f}")
    print(f"Score Reranker : {result['rerank_score']:.6f}")
    print(f"Page : {result['metadata']['page']}")
    print(f"Texte : {result['text'][:400]}")
    print("-" * 60)

# context builder
context_data = build_context(candidates=reranked_results)

print("\n" + "=" * 70)
print("CONTEXTE CONSTRUIT")
print("=" * 70)

print(context_data["context"])

print("\nSOURCES :")
for source in context_data["sources"]:
    print(source)

print("\nNombre de chunks utilisés :", context_data["chunks_used"])

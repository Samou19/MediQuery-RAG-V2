from app.services.fusion import reciprocal_rank_fusion
from app.services.retrieval import dense_search
from app.services.sparse_retrieval import SparseRetriever

question = (
    "Quelles sont les étapes du parcours de soins "
    "d'un patient adulte vivant avec un diabète de type 2 ?"
)

# 1. Recherche Dense
dense_results = dense_search(question, top_k=5)

# 2. Recherche Sparse
sparse_retriever = SparseRetriever()

try:
    sparse_retriever.build_index()
    sparse_results = sparse_retriever.search(question, top_k=5)
finally:
    sparse_retriever.close()

# 3. Fusion RRF
fused_results = reciprocal_rank_fusion(
    dense_results=dense_results, sparse_results=sparse_results, k=60, top_k=5
)

# 4. Affichage
print("\n========== RÉSULTATS RRF ==========\n")

for rank, result in enumerate(fused_results, start=1):
    print(f"Rang : {rank}")
    print(f"ID : {result['id']}")
    print(f"Score RRF : {result['rrf_score']:.6f}")
    print(f"Page : {result['metadata']['page']}")
    print(f"Classement : {result['ranks']}")
    print(f"Sources : {result['sources']}")
    print(f"Texte : {result['text'][:300]}")
    print("-" * 60)

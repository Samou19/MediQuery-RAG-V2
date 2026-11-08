from app.services.sparse_retrieval import SparseRetriever

question = (
    "Quelles sont les étapes du parcours de soins "
    "d'un patient adulte vivant avec un diabète de type 2 ?"
)

retriever = SparseRetriever()

try:
    # Construire l'index BM25
    retriever.build_index()

    # Effectuer la recherche
    results = retriever.search(question=question, top_k=5)

    print("\nQUESTION :", question)
    print("\nNOMBRE DE RÉSULTATS :", len(results))

    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"RÉSULTAT N° {rank}")
        print("=" * 70)

        print("ID :", result["id"])
        print("Score BM25 :", round(result["score"], 4))
        print("Page :", result["metadata"]["page"])
        print("Chunk ID :", result["metadata"]["chunk_id"])

        print("\nCONTENU :")
        print(result["text"][:800])

finally:
    retriever.close()

from app.services.retrieval import dense_search

question = (
    "Quelles sont les étapes du parcours de soins "
    "d'un patient adulte vivant avec un diabète de type 2 ?"
)

results = dense_search(question=question, top_k=5)

print("\nQUESTION :", question)
print("\nNOMBRE DE RÉSULTATS :", len(results))

for rank, result in enumerate(results, start=1):
    print("\n" + "=" * 70)
    print(f"RÉSULTAT N° {rank}")
    print("=" * 70)

    print("ID :", result["id"])
    print("Score :", round(result["score"], 4))
    print("Page :", result["metadata"]["page"])
    print("Chunk ID :", result["metadata"]["chunk_id"])

    print("\nCONTENU :")
    print(result["text"][:800])

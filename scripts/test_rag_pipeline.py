from app.pipelines.rag_pipeline import rag_query

if __name__ == "__main__":
    question = (
        "Quelles sont les étapes du parcours de soins "
        "d'un patient adulte vivant avec un diabète de type 2 ?"
    )

    result = rag_query(question)

    print("\n" + "=" * 60)
    print("QUESTION")
    print("=" * 60)
    print(result["question"])

    print("\n" + "=" * 60)
    print("RÉPONSE MEDIQUERY")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)

    for source in result["sources"]:
        print(
            f"Document : {source['filename']} | "
            f"Page : {source['page']} | "
            f"Chunk : {source['chunk_id']}"
        )

    print("\n" + "=" * 60)
    print("MÉTADONNÉES")
    print("=" * 60)
    print("Chunks utilisés :", result["chunks_used"])
    print("Modèle :", result["model"])
    print("Consommation :", result["usage"])

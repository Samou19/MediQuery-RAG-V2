from app.repositories.qdrant_repository import QdrantRepository

repository = QdrantRepository()

try:
    # 1. Vérifier le nombre total de points
    total = repository.count_points()
    print("Nombre total de points :", total)

    # 2. Récupérer les 5 premiers points
    response = repository.client.scroll(
        collection_name=repository.collection_name,
        limit=5,
        with_payload=True,
        with_vectors=True,
    )

    points, next_offset = response

    print("\nPOINTS RÉCUPÉRÉS :", len(points))

    # 3. Examiner chaque point
    for point in points:
        print("\n" + "=" * 70)
        print("POINT ID :", point.id)
        print("=" * 70)

        # Vérification du vecteur
        vector = point.vector

        print("Type du vecteur :", type(vector))
        print("Dimension :", len(vector))
        print("Premières valeurs :", vector[:5])

        # Vérification du payload
        payload = point.payload or {}

        print("\nTEXTE :")
        print(payload.get("text", "")[:500])

        print("\nMÉTADONNÉES :")
        print("Fichier :", payload.get("filename"))
        print("Page :", payload.get("page"))
        print("Chunk ID :", payload.get("chunk_id"))

finally:
    repository.close()

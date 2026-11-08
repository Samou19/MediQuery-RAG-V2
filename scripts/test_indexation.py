import json
from pathlib import Path

from app.repositories.qdrant_repository import QdrantRepository

# 1. Charger les embeddings sauvegardés
input_path = Path("data/processed/embedded_chunks.json")

with input_path.open("r", encoding="utf-8") as file:
    embedded_chunks = json.load(file)

print("Nombre de chunks chargés :", len(embedded_chunks))


# 2. Initialiser le repository
repository = QdrantRepository()

try:
    # 3. Créer la collection si nécessaire
    repository.create_collection()

    # 4. Insérer les points
    repository.upsert_chunks(embedded_chunks, batch_size=64)

    # 5. Vérifier le résultat
    info = repository.get_collection_info()
    count = repository.count_points()

    print("\nSTATISTIQUES QDRANT")
    print("Collection :", repository.collection_name)
    print("Points indexés :", count)
    print("Dimension :", repository.dimension)
    print("Statut :", info.status)

finally:
    repository.close()

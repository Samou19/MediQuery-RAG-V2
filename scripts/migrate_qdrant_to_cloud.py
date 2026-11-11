import logging
import os
import sys
from pathlib import Path

from qdrant_client import QdrantClient, models

from app.core.config import get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def migrate_collection():
    settings = get_settings()

    # Connexion à Qdrant local
    local_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=60,
    )

    # Connexion à Qdrant Cloud
    cloud_url = os.environ["QDRANT_CLOUD_URL"]
    cloud_api_key = os.environ["QDRANT_CLOUD_API_KEY"]

    cloud_client = QdrantClient(
        url=cloud_url,
        api_key=cloud_api_key,
        timeout=60,
    )

    collection = settings.QDRANT_COLLECTION

    try:
        # 1. Vérifier la collection source
        source_info = local_client.get_collection(collection)
        expected_points = source_info.points_count

        logger.info("Collection source : %s", collection)
        logger.info("Nombre de points : %s", expected_points)

        if expected_points == 0:
            raise ValueError("La collection source est vide.")

        # 2. Ne jamais écraser une collection Cloud existante
        if cloud_client.collection_exists(collection):
            raise RuntimeError(
                f"La collection {collection} existe déjà sur Qdrant Cloud. "
                "Migration interrompue pour éviter tout écrasement."
            )

        # 3. Créer la collection Cloud avec la même configuration
        cloud_client.create_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )

        logger.info("Collection Cloud créée.")

        # 4. Lire et transférer les points par lots
        offset = None
        transferred = 0

        while True:
            points, next_offset = local_client.scroll(
                collection_name=collection,
                limit=BATCH_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            if not points:
                break

            cloud_client.upsert(
                collection_name=collection,
                points=[
                    models.PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=point.payload,
                    )
                    for point in points
                ],
                wait=True,
            )

            transferred += len(points)

            logger.info(
                "Transfert : %s/%s points",
                transferred,
                expected_points,
            )

            if next_offset is None:
                break

            offset = next_offset

        # 5. Vérifier le résultat
        cloud_count = cloud_client.count(
            collection_name=collection,
            exact=True,
        ).count

        logger.info("Points locaux : %s", expected_points)
        logger.info("Points Cloud : %s", cloud_count)

        if cloud_count != expected_points:
            raise RuntimeError(
                "Le nombre de points transférés ne correspond pas "
                "au nombre de points de la source."
            )

        logger.info("Migration terminée avec succès.")

    finally:
        local_client.close()
        cloud_client.close()


if __name__ == "__main__":
    migrate_collection()

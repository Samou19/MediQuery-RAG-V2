import logging

from qdrant_client import QdrantClient, models

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class QdrantRepository:
    """Centralise les opérations Qdrant de MediQuery V2."""

    def __init__(self):
        self.settings = get_settings()

        self.client = QdrantClient(
            url=self.settings.QDRANT_URL,
            api_key=self.settings.QDRANT_API_KEY,
            timeout=30,
        )

        self.collection_name = self.settings.QDRANT_COLLECTION
        self.dimension = self.settings.EMBEDDING_DIMENSION

    def create_collection(self) -> None:
        """Crée la collection si elle n'existe pas."""

        if self.client.collection_exists(self.collection_name):
            logger.info("La collection %s existe déjà.", self.collection_name)
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.dimension, distance=models.Distance.COSINE
            ),
        )

        logger.info(
            "Collection %s créée (dimension=%s, distance=Cosine).",
            self.collection_name,
            self.dimension,
        )

    def upsert_chunks(self, embedded_chunks: list[dict], batch_size: int = 64) -> None:
        """Insère ou met à jour les chunks vectorisés."""

        if not embedded_chunks:
            logger.warning("Aucun chunk à indexer.")
            return

        if batch_size <= 0:
            raise ValueError("batch_size doit être positif.")

        # Vérifier la dimension avant toute insertion
        for chunk in embedded_chunks:
            vector = chunk.get("vector", [])

            if len(vector) != self.dimension:
                raise ValueError(
                    f"Dimension incorrecte pour le chunk "
                    f"{chunk.get('chunk_id')} : {len(vector)}"
                )

        # Vérifier l'unicité des identifiants
        ids = [chunk["chunk_id"] for chunk in embedded_chunks]

        if len(ids) != len(set(ids)):
            raise ValueError("Les chunk_id doivent être uniques.")

        total = len(embedded_chunks)

        for start in range(0, total, batch_size):
            batch = embedded_chunks[start : start + batch_size]

            points = []

            for chunk in batch:
                metadata = chunk.get("metadata", {})

                payload = {
                    "text": chunk["text"],
                    "filename": metadata.get("filename"),
                    "page": metadata.get("page"),
                    "chunk_id": chunk["chunk_id"],
                }

                points.append(
                    models.PointStruct(
                        id=chunk["chunk_id"], vector=chunk["vector"], payload=payload
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name, points=points, wait=True
            )

            logger.info(
                "Indexation : %s/%s points traités",
                min(start + len(batch), total),
                total,
            )

        logger.info("Indexation terminée : %s points.", total)

    def get_collection_info(self):
        """Retourne les informations de la collection."""

        return self.client.get_collection(collection_name=self.collection_name)

    def count_points(self) -> int:
        """Retourne le nombre exact de points dans la collection."""

        result = self.client.count(collection_name=self.collection_name, exact=True)

        return result.count

    def close(self) -> None:
        """Ferme la connexion au client Qdrant."""

        self.client.close()

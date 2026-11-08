import logging

import voyageai

from app.core.config import get_settings
from app.repositories.qdrant_repository import QdrantRepository

logger = logging.getLogger(__name__)


def dense_search(question: str, top_k: int = 5) -> list[dict]:
    """
    Recherche les chunks les plus pertinents dans Qdrant
    à partir de l'embedding de la question.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    if top_k <= 0:
        raise ValueError("top_k doit être positif.")

    settings = get_settings()

    # 1. Transformer la question en embedding
    voyage_client = voyageai.Client(api_key=settings.VOYAGE_API_KEY)

    response = voyage_client.embed(
        texts=[question],
        model=settings.VOYAGE_EMBEDDING_MODEL,
        input_type="query",
        output_dimension=settings.EMBEDDING_DIMENSION,
        output_dtype="float",
        truncation=False,
    )

    query_vector = response.embeddings[0]

    # 2. Interroger Qdrant
    repository = QdrantRepository()

    try:
        search_response = repository.client.query_points(
            collection_name=repository.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # 3. Structurer les résultats
        results = []

        for point in search_response.points:
            payload = point.payload or {}

            results.append(
                {
                    "id": point.id,
                    "score": point.score,
                    "text": payload.get("text", ""),
                    "metadata": {
                        "filename": payload.get("filename"),
                        "page": payload.get("page"),
                        "chunk_id": payload.get("chunk_id"),
                    },
                }
            )

        logger.info(
            "Recherche Dense terminée : %s résultats pour la question.", len(results)
        )

        return results

    finally:
        repository.close()

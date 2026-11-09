import logging

import voyageai

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def generate_embeddings(
    chunks: list[dict],
    model: str | None = None,
    dimension: int | None = None,
    batch_size: int = 64,
) -> list[dict]:

    if not chunks:
        logger.warning("Aucun chunk à vectoriser.")
        return []

    if batch_size <= 0:
        raise ValueError("batch_size doit être positif.")

    # Récupération de la configuration centralisée
    settings = get_settings()

    model = model or settings.VOYAGE_EMBEDDING_MODEL
    dimension = dimension or settings.EMBEDDING_DIMENSION

    client = voyageai.Client(api_key=settings.VOYAGE_API_KEY)

    embedded_chunks = []
    total_tokens = 0

    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_number, start in enumerate(range(0, len(chunks), batch_size), start=1):
        batch = chunks[start : start + batch_size]
        texts = [chunk["text"] for chunk in batch]

        logger.info(
            "Embedding lot %s/%s (%s chunks)", batch_number, total_batches, len(batch)
        )

        try:
            response = client.embed(
                texts=texts,
                model=model,
                input_type="document",
                output_dimension=dimension,
                output_dtype="float",
                truncation=False,
            )

        except Exception:
            logger.exception("Erreur lors de la génération du lot %s", batch_number)
            raise

        if len(response.embeddings) != len(batch):
            raise RuntimeError("Le nombre de vecteurs retournés est incorrect.")

        total_tokens += response.total_tokens

        for chunk, vector in zip(batch, response.embeddings, strict=True):
            if len(vector) != dimension:
                raise ValueError(f"Dimension incorrecte : {len(vector)}")

            embedded_chunks.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"].copy(),
                    "vector": vector,
                }
            )

    logger.info(
        "Embedding terminé : %s chunks, %s tokens utilisés",
        len(embedded_chunks),
        total_tokens,
    )

    return embedded_chunks

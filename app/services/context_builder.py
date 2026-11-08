import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def build_context(candidates: list[dict], max_chunks: int | None = None) -> dict:
    """
    Construit un contexte structuré à partir des résultats
    du retrieval et du reranking.

    Args:
        candidates: Liste des chunks classés par pertinence.
        max_chunks: Nombre maximum de chunks à conserver.

    Returns:
        Un dictionnaire contenant le contexte, les sources
        et le nombre de chunks utilisés.
    """

    if not candidates:
        return {"context": "", "sources": [], "chunks_used": 0}

    settings = get_settings()

    if max_chunks is None:
        max_chunks = settings.TOP_K_RERANK

    if max_chunks <= 0:
        raise ValueError("max_chunks doit être positif.")

    selected_chunks = []
    seen_ids = set()

    # 1. Validation et sélection des chunks
    for candidate in candidates:
        chunk_id = candidate.get("id")
        text = candidate.get("text", "")

        if chunk_id is None or not isinstance(text, str):
            continue

        text = text.strip()

        if not text:
            continue

        # Éviter les doublons
        if chunk_id in seen_ids:
            continue

        seen_ids.add(chunk_id)

        metadata = candidate.get("metadata") or {}

        selected_chunks.append(
            {
                "id": chunk_id,
                "text": text,
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "chunk_id": metadata.get("chunk_id", chunk_id),
                "rerank_score": candidate.get("rerank_score"),
            }
        )

        if len(selected_chunks) >= max_chunks:
            break

    # 2. Construction du contexte et des sources
    context_parts = []
    sources = []

    for rank, chunk in enumerate(selected_chunks, start=1):
        filename = chunk["filename"] or "Document non précisé"
        page = chunk["page"] if chunk["page"] is not None else "Non précisée"

        context_parts.append(
            f"[Source {rank}]\n"
            f"Document : {filename}\n"
            f"Page : {page}\n"
            f"Contenu :\n{chunk['text']}"
        )

        sources.append(
            {
                "filename": chunk["filename"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "rerank_score": chunk["rerank_score"],
            }
        )

    context = "\n\n".join(context_parts)

    logger.info(
        "Contexte construit : %s chunks utilisés sur %s candidats.",
        len(selected_chunks),
        len(candidates),
    )

    return {"context": context, "sources": sources, "chunks_used": len(selected_chunks)}

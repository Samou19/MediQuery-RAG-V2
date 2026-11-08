import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def merge_small_chunks(
    chunks: list[dict],
    chunk_size: int = 1000,
    min_chunk_size: int = 200,
    chunk_overlap: int = 150,
) -> list[dict]:
    """
    Fusionne les petits chunks avec un voisin de la même page.
    Conserve les métadonnées et respecte la taille maximale.
    """

    merged_chunks = []
    i = 0

    while i < len(chunks):
        current = chunks[i].copy()
        current_text = current["text"]

        # Chunk suffisamment grand : on le conserve
        if len(current_text) >= min_chunk_size:
            merged_chunks.append(current)
            i += 1
            continue

        # Essayer de fusionner avec le chunk suivant
        if i + 1 < len(chunks):
            next_chunk = chunks[i + 1]

            same_page = current["metadata"].get("page") == next_chunk["metadata"].get(
                "page"
            )

            if same_page:
                next_text = next_chunk["text"]

                # Rechercher un éventuel chevauchement
                max_overlap = min(chunk_overlap, len(current_text), len(next_text))

                overlap = 0

                for size in range(max_overlap, 0, -1):
                    if current_text.endswith(next_text[:size]):
                        overlap = size
                        break

                remaining_text = next_text[overlap:].lstrip()

                separator = "\n\n" if not current_text.endswith("\n") else "\n"

                combined_text = current_text.rstrip() + separator + remaining_text

                if len(combined_text) <= chunk_size:
                    current["text"] = combined_text
                    merged_chunks.append(current)
                    i += 2
                    continue

        # Si la fusion avec le suivant est impossible,
        # essayer avec le précédent.
        if merged_chunks:
            previous = merged_chunks[-1]

            same_page = previous["metadata"].get("page") == current["metadata"].get(
                "page"
            )

            if same_page:
                previous_text = previous["text"]
                combined_text = previous_text.rstrip() + "\n\n" + current_text.lstrip()

                if len(combined_text) <= chunk_size:
                    previous["text"] = combined_text
                    i += 1
                    continue

        # Aucun voisin compatible : conserver le petit chunk
        merged_chunks.append(current)
        i += 1

    return merged_chunks


def create_chunks(
    documents: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    min_chunk_size: int = 200,
) -> list[dict]:

    if chunk_size <= 0:
        raise ValueError("chunk_size doit être positif.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap doit être positif et inférieur à chunk_size.")

    if min_chunk_size <= 0 or min_chunk_size > chunk_size:
        raise ValueError(
            "min_chunk_size doit être positif et inférieur ou égal à chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        length_function=len,
        is_separator_regex=False,
    )

    chunks = []

    for document in documents:
        text = document.get("text", "").strip()

        if not text:
            continue

        metadata = document.get("metadata", {})

        text_chunks = splitter.split_text(text)

        for text_chunk in text_chunks:
            chunks.append({"text": text_chunk, "metadata": metadata.copy()})

    # Fusion des petits chunks
    chunks = merge_small_chunks(
        chunks,
        chunk_size=chunk_size,
        min_chunk_size=min_chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # Réattribuer des identifiants uniques après fusion
    for chunk_id, chunk in enumerate(chunks):
        chunk["chunk_id"] = chunk_id
        chunk["metadata"]["chunk_id"] = chunk_id

    logger.info(
        "Chunking terminé : %s chunks générés à partir de %s pages",
        len(chunks),
        len(documents),
    )

    return chunks

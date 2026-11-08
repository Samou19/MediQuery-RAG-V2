import logging
import re

logger = logging.getLogger(__name__)


def clean_text(text: str, page_number: int | None = None) -> str:
    if not text:
        return ""

    # Normalisation des retours à la ligne
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Suppression des caractères invisibles
    text = text.replace("\u00ad", "")
    text = text.replace("\xa0", " ")

    # Suppression de l'en-tête répétitif HAS
    text = re.sub(
        r"HAS\s*[•·]\s*Parcours de soins du patient adulte "
        r"vivant avec un diabète de type 2\s*[•·]\s*juin 2025",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Suppression du numéro de page en première ou dernière ligne
    lines = text.split("\n")

    if page_number is not None:
        lines = text.split("\n")

        # Supprimer le numéro de page isolé,
        # même si des lignes vides le précèdent ou le suivent.
        non_empty_indices = [i for i, line in enumerate(lines) if line.strip()]

        if non_empty_indices:
            first = non_empty_indices[0]
            last = non_empty_indices[-1]

            if lines[first].strip() == str(page_number):
                lines.pop(first)

            non_empty_indices = [i for i, line in enumerate(lines) if line.strip()]

            if non_empty_indices:
                last = non_empty_indices[-1]

                if lines[last].strip() == str(page_number):
                    lines.pop(last)

        text = "\n".join(lines)

    # Reconstitution des mots coupés en fin de ligne.
    # Exemple : dia-\nbète devient diabète.
    text = re.sub(r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ])-\n(?=[a-zà-öø-ÿ])", "", text)

    # Nettoyage des espaces
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_documents(documents: list[dict]) -> list[dict]:
    cleaned_documents = []

    for document in documents:
        metadata = document.get("metadata", {})
        page_number = metadata.get("page")

        cleaned_content = clean_text(document.get("text", ""), page_number=page_number)

        if not cleaned_content:
            logger.warning("Page %s vide après nettoyage", page_number)
            continue

        cleaned_documents.append({"text": cleaned_content, "metadata": metadata.copy()})

    logger.info(
        "Nettoyage terminé : %s pages conservées sur %s",
        len(cleaned_documents),
        len(documents),
    )

    return cleaned_documents

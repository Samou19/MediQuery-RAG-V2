import logging
from pathlib import Path

import pymupdf  # PyMuPDF

logger = logging.getLogger(__name__)


def extract_pdf(pdf_path: str | Path) -> list[dict]:
    """
    Extrait le texte d'un PDF page par page.

    Args:
        pdf_path: chemin du fichier PDF.

    Returns:
        Liste de documents contenant le texte et les métadonnées.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Le fichier doit être au format PDF.")

    documents = []

    try:
        with pymupdf.open(pdf_path) as pdf:
            logger.info("Début extraction : %s (%s pages)", pdf_path.name, len(pdf))

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if not text:
                    logger.warning("Page %s vide dans %s", page_number, pdf_path.name)
                    continue

                documents.append(
                    {
                        "text": text,
                        "metadata": {"filename": pdf_path.name, "page": page_number},
                    }
                )

            logger.info("Extraction terminée : %s pages extraites", len(documents))

    except Exception:
        logger.exception("Erreur lors de l'extraction de %s", pdf_path.name)
        raise

    return documents

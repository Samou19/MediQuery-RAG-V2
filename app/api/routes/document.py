import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.api.schemas.document import (
    DocumentDeleteResponse,
    DocumentInfo,
    DocumentListResponse,
    DocumentUploadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 Mo


def get_document_path(filename: str) -> Path:
    """Construit un chemin sécurisé vers un document."""

    if Path(filename).name != filename or filename in {"", ".", ".."}:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide.")

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400, detail="Seuls les fichiers PDF sont acceptés."
        )

    return UPLOAD_DIR / filename


# 1. Déposer un document PDF
@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile):

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400, detail="Seuls les fichiers PDF sont acceptés."
        )

    filename = Path(file.filename).name
    destination = get_document_path(filename)

    if destination.exists():
        raise HTTPException(
            status_code=409, detail="Un fichier portant ce nom existe déjà."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="Le fichier dépasse la taille maximale de 20 Mo."
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400, detail="Le fichier fourni n'est pas un PDF valide."
        )

    destination.write_bytes(content)

    logger.info("Document reçu : %s (%s octets)", filename, len(content))

    return DocumentUploadResponse(
        filename=filename,
        content_type=file.content_type or "application/pdf",
        size_bytes=len(content),
        status="uploaded",
        message="Document reçu et enregistré avec succès.",
    )


# 2. Lister les documents
@router.get("/", response_model=DocumentListResponse)
def list_documents():

    documents = []

    for file_path in UPLOAD_DIR.glob("*.pdf"):
        if not file_path.is_file():
            continue

        documents.append(
            DocumentInfo(
                filename=file_path.name,
                size_bytes=file_path.stat().st_size,
                content_type="application/pdf",
                status="uploaded",
            )
        )

    return DocumentListResponse(total=len(documents), documents=documents)


# 3. Consulter un document
@router.get("/{filename}", response_model=DocumentInfo)
def get_document(filename: str):

    file_path = get_document_path(filename)

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Document introuvable.")

    return DocumentInfo(
        filename=file_path.name,
        size_bytes=file_path.stat().st_size,
        content_type="application/pdf",
        status="uploaded",
    )


# 4. Supprimer un document
@router.delete("/{filename}", response_model=DocumentDeleteResponse)
def delete_document(filename: str):

    file_path = get_document_path(filename)

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Document introuvable.")

    file_path.unlink()

    logger.info("Document supprimé : %s", filename)

    return DocumentDeleteResponse(
        filename=filename, status="deleted", message="Document supprimé avec succès."
    )

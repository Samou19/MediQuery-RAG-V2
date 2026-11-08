import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.pipelines.rag_pipeline import rag_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint permettant d'interroger MediQuery V2.
    """

    try:
        # Exécution du pipeline RAG complet
        result = rag_query(request.question)

        # Transformation des sources au format API
        sources = [
            {
                "filename": source["filename"],
                "page": source["page"],
                "chunk_id": source.get("chunk_id"),
                "score": source.get("rerank_score"),
            }
            for source in result["sources"]
        ]

        return ChatResponse(
            question=result["question"],
            answer=result["answer"],
            sources=sources,
            status="success",
            timings_ms=result["timings_ms"],
        )

    except Exception:
        logger.exception("Erreur lors du traitement de la question.")

        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors du traitement de votre question.",
        )

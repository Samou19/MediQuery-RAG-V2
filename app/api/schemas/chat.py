from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question posée par l'utilisateur",
    )


class SourceDocument(BaseModel):
    filename: str
    page: int | None = None
    chunk_id: int | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceDocument] = Field(default_factory=list)
    status: str
    timings_ms: dict[str, float] = Field(default_factory=dict)

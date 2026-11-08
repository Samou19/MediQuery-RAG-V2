from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    status: str
    message: str


class DocumentInfo(BaseModel):
    filename: str
    size_bytes: int
    content_type: str
    status: str


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentInfo]


class DocumentDeleteResponse(BaseModel):
    filename: str
    status: str
    message: str

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Auth ---
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# --- Documents ---
class DocumentIngestRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, description="Raw text content to ingest and index")


class DocumentResponse(BaseModel):
    id: str
    title: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Chat / RAG ---
class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    document_id: str | None = Field(
        default=None, description="Optional: restrict retrieval to a single document"
    )


class RetrievedChunk(BaseModel):
    document_id: str
    chunk_index: int
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[RetrievedChunk]


# --- Errors ---
class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None

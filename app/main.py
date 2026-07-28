from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.middleware import ExceptionLoggingMiddleware
from app.routers import auth, chat, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # NOTE: create_all() is convenient for local dev / this assignment.
    # In a real production setup, use Alembic migrations instead so schema
    # changes are versioned and reversible.
    await init_db()
    yield


app = FastAPI(
    title="FastAPI + AI RAG Backend",
    description="JWT-authenticated backend with document ingestion and a RAG-powered /chat endpoint.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(ExceptionLoggingMiddleware)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

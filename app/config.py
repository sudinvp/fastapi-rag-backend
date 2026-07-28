from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:sudin@localhost:5432/rag_db"
    database_url_sync: str = "postgresql+psycopg2://postgres:sudin@localhost:5432/rag_db"

    # JWT Authentication
    jwt_secret_key: str = "mysecretkey12345678"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Google Gemini
    gemini_api_key: str = ""
    llm_model: str = "gemini-flash-latest"

    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Chunking / Retrieval
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 4

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
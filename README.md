# FastAPI + AI (RAG) Backend

## Overview

This project is a FastAPI backend that implements a Retrieval-Augmented Generation (RAG) system. It allows users to register, upload documents, and ask questions based on the uploaded documents using Google Gemini AI.

---

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Google Gemini API
- Sentence Transformers
- Docker
- Pytest

---
## Project Structure

```text
app/
├── routers/
├── services/
├── models.py
├── schemas.py
├── auth.py
├── database.py
├── middleware.py
├── config.py
└── main.py

tests/
├── test_auth.py
└── test_chunking.py
```
---

## Setup

### Clone the project

```bash
git clone <repository-url>
cd fastapi-rag-backend
```

### Install dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configure `.env`

```env
DATABASE_URL=your_database_url
DATABASE_URL_SYNC=your_database_url_sync

JWT_SECRET_KEY=your_secret_key

GEMINI_API_KEY=your_api_key
LLM_MODEL=gemini-flash-latest
```

### Run the project

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## API Endpoints

- **POST /auth/signup** – Register a new user
- **POST /auth/login** – Login and get JWT token
- **POST /documents/** – Upload a document
- **GET /documents/** – View uploaded documents
- **DELETE /documents/{id}** – Delete a document
- **POST /chat/** – Ask questions using RAG
- **POST /chat/stream** – Stream AI responses
- **GET /health** – Health check

---

## RAG Workflow

1. Upload a document.
2. Split the document into chunks.
3. Generate embeddings.
4. Store chunks in PostgreSQL.
5. Retrieve relevant chunks.
6. Send context to Gemini.
7. Return the AI-generated answer.

---

## Run Tests

```bash
pytest
```

---

## Future Improvements

- Use pgvector for faster search
- Add Alembic migrations
- Add Redis caching
- Add rate limiting
- Improve scalability with Celery
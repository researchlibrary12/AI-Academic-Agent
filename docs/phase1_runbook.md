# Phase 1 Runbook

## 1) Configure environment

Backend `.env` (copy from `.env.example`):
- `OPENAI_API_KEY`
- `MODEL_PROVIDER=openai`
- `MODEL_NAME=gpt-4.1`
- `EMBEDDING_MODEL=text-embedding-3-large`
- `CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json`
- `JWT_ISSUER=https://<your-clerk-domain>`
- `JWT_AUDIENCE=<your-api-audience>` (optional, but recommended)

Frontend `.env.local`:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

## 2) Start backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --reload --port 8000
```

## 3) Start frontend

```bash
cd frontend
npm install
npm run dev
```

## 4) Test protected APIs

Use a valid Clerk JWT:

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:8000/api/v1/auth/me
```

Upload a PDF/text document:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <JWT>" \
  -F "file=@/path/to/document.pdf" \
  -F "faculty=Engineering" \
  -F "course=Computer Science" \
  -F "module=Data Structures" \
  -F "topic=Trees" \
  -F "year=2026" \
  -F "document_type=Past Paper"
```

Run a RAG query:

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "question":"What tree traversal questions appear repeatedly?",
    "metadata_filter":{"module":"Data Structures"}
  }'
```

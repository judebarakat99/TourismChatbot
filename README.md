# TourismChatbot

A small UK tourism question-answering chatbot backend using Qdrant for vector search and OpenAI for embeddings and LLM responses.

## Features ✅

- **FastAPI** backend exposing a streaming chat endpoint (`/chat/stream`) 🔁
- **Qdrant** vector store for document similarity search 🔎
- **Data ingestion** script to embed local Markdown resources 📄

---

## Quick start (development) 🔧

1. Create a `.env` file in the `backend/` directory with:

```env
OPENAI_API_KEY=sk-...
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=tourism_uk
CORS_ORIGINS=*
APP_NAME=Tourism Bot API
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

2. Start Qdrant (from `backend/`):

```bash
cd backend
docker-compose up -d
```

3. (Optional) Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

4. Ingest data (Markdown files in `data/uk`):

```bash
python backend/scripts/ingest.py --path data/uk
```

5. Run the API:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Check health:

```bash
curl http://localhost:8000/health
```

---

## Example request 💬

POST JSON to `/chat/stream` with fields `message` and `session_id`. The endpoint streams SSE events including `token` events and a `meta` event containing `sources`.

---

## Project layout 🔧

- `backend/` — FastAPI app, Docker Compose, ingestion script, requirements
- `data/uk/` — Markdown sources (attractions, etiquette, events, seasons, transport)
- `docs/`, `index.html`, `app.js` — static frontend assets

> ⚠️ **Note:** Make sure `OPENAI_API_KEY` is set before running ingestion or the API.

---

## Contributing & License

Contributions welcome — open an issue or PR. Add license information here.

# TourismChatbot Operations Guide

This playbook captures the day-to-day operational steps for running the stack.

## Setup Overview
- **Services:** FastAPI backend (LangChain RAG), Qdrant vector store, Next.js frontend
- **Dependencies:** Docker + Docker Compose, Python 3.11+ for local dev, Node.js 20+ for the frontend
- **Configs:** Copy an `.env` file next to `backend/app/main.py` before starting the backend; templates live in [docs/environment/ENVIRONMENT_GUIDE.md](docs/environment/ENVIRONMENT_GUIDE.md)

## Run the full stack with Docker Compose
1. Copy [docs/environment/.env.example](docs/environment/.env.example) to `backend/.env` and fill in your Azure OpenAI + Qdrant details.
2. From the repository root, build and start everything:
   ```bash
   docker compose up --build
   ```
3. Optional: run detached via `docker compose up -d` and later `docker compose down`.
4. Default endpoints:
   - Qdrant → http://localhost:6333
   - FastAPI → http://localhost:8000
   - Next.js → http://localhost:3000

### Single-service compose wrappers
Located in `deploy/`, each wrapper reuses the main compose file via `extends`:

| Use case | Command |
| --- | --- |
| Qdrant only | `docker compose -f deploy/qdrant.compose.yml up` |
| Qdrant + backend | `docker compose -f deploy/backend.compose.yml up --build` |
| Full stack (frontend included) | `docker compose -f deploy/frontend.compose.yml up --build` |
| Strict startup order (Qdrant → backend → frontend) | `docker compose -f deploy/stack.compose.yml up --build` |

Add `-d` to any command to run in the background.

## Local development workflow
### Backend (FastAPI + LangChain)
1. `cd backend`
2. `python -m venv .venv && .venv\Scripts\activate` (PowerShell) or `source .venv/bin/activate` (macOS/Linux)
3. `pip install -r requirements.txt`
4. Copy [docs/environment/.env.example](docs/environment/.env.example) to `.env` and update values.
5. Ensure Qdrant is running (Docker: `docker compose up -d qdrant` from `backend/`).
6. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend (Next.js)
1. `cd frontend`
2. `npm install`
3. `npm run dev` → http://localhost:3000

## Data ingestion
The backend auto-loads `.md`/`.txt` under `backend/data` on startup. To control ingestion manually:
```bash
python backend/scripts/ingest.py --path backend/data/italy
```
- Override the source directory via the `DATA_DIR` env var.
- Each chunk upsert uses deterministic IDs, so repeated ingests update existing vectors without duplication.

## Troubleshooting quick hits
- **Pydantic warning on Python 3.14+:** prefer Python 3.11–3.12 until Pydantic v2 fully supports 3.14.
- **Port already in use:** adjust `ports` in `docker-compose.yml` or stop the conflicting service.
- **Missing Azure credentials:** run `python backend/azure_diagnostic.py` to verify env vars.

## Additional references
- Environment templates → [docs/environment/ENVIRONMENT_GUIDE.md](docs/environment/ENVIRONMENT_GUIDE.md)
- API contract + FastAPI auto-docs → [docs/API.md](docs/API.md)
- End-user guide for the chat UI → [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

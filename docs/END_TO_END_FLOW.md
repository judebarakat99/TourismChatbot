# End-to-End Flow Guide

This document links the frontend, backend, and vector database subsystems so newcomers can trace a chat request from the browser to the final response.

## High-Level Architecture
```text
[User Browser]
   |
   v
[Next.js Frontend (Routey)] --(REST/SSE)--> [FastAPI Backend]
   |                                          |
   |                                          +--> [Qdrant Vector DB]
   |                                          |
   |                                          +--> [Azure OpenAI (Chat + Embeddings)]
   v
[Rendered Streaming Chat UI]
```

## Request/Response Swimlane
```text
User            Frontend (Next.js)            Backend (FastAPI)               Qdrant / Azure
│                    │                              │                               │
│  Chat input ─────> │                              │                               │
│                    │ chatWithStream() fetch       │                               │
│                    │───────────────SSE POST─────>│                               │
│                    │                              │ retrieve_context()            │
│                    │                              │────────similarity search────> │ (Qdrant)
│                    │                              │<────chunks + metadata──────── │
│                    │                              │ stream_answer() builds prompt │
│                    │                              │────────prompt tokens────────> │ (Azure Chat)
│                    │                              │<────LLM tokens streamed────── │
│                    │<─────────event: token────────│                               │
│UI updates in real time                             │                               │
│                    │<─────────event: meta─────────│                               │
│                    │                              │ sessions state persisted      │
│ Rendered answer <──│                              │                               │
```

## Deployment Touchpoints
- `deploy/stack.compose.yml` orchestrates backend, frontend, and Qdrant containers; ensure matching env vars across services.
- Backend expects Azure OpenAI credentials and Qdrant URL configured via `.env` or Docker secrets.
- Frontend reads `NEXT_PUBLIC_API_URL` to target the running FastAPI instance.
- Health checks: `frontend` polls `/health`; `docker compose ps` should show `qdrant`, `backend`, and `frontend` healthy.

## Key Cross-Cutting Concerns
- **Session IDs:** Generated client-side per conversation and reused on every call so the backend can accumulate chat history.
- **Sources:** Retrieval layer tags snippets with file paths; the backend streams them via `event: meta`, enabling the UI to show citations.
- **Localization:** Language preference stored in browser; backend prompt includes `{language}` and returns translated responses.
- **Streaming:** All layers (Azure chat, FastAPI, fetch reader) operate in streaming mode to minimize latency and keep the UI reactive.

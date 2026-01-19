# Backend Flow Guide

This document illustrates how the FastAPI backend handles incoming chat requests from the Routey frontend.

## Request-to-Response Flowchart
```text
[Client hits /chat/stream]
        |
        v
[FastAPI parses ChatRequest (message, session_id, language)]
        |
        v
[Lookup in-memory session history for session_id]
        |
        v
[Flatten history -> chat_history text block]
        |
        v
[Call ask_tourism_bot(question, chat_history, language)]
        |
        v
[retrieve_context() pulls top-k chunks from Qdrant]
        |
        v
[stream_answer() renders prompt + streams Azure Chat completion]
        |
        v
[Yield SSE `event: token` for each chunk from LLM]
        |
        v
[Accumulate assistant text + send meta event w/ metadata]
        |
        v
[Persist user + assistant messages back into sessions]
        |
        v
[StreamingResponse closes when model finishes]
```

## Supporting Endpoints / Flows
```text
[GET /health] -> [Return status + rag flag]
[DELETE /conversations/{id}] -> [Remove stored conversation if present]
[GET /chat (legacy)] -> [Uses GLOBAL_SESSION_ID but same streaming pipeline]
```

## Step Notes
- Core FastAPI logic lives in backend/app/main.py.
- ask_tourism_bot() (backend/app/langchain/rag.py) orchestrates context retrieval and LLM streaming.
- stream_answer() (backend/app/langchain/chain.py) builds prompt input (question, context, chat history, date, language) and streams Azure Chat tokens.
- CORS is opened to localhost origins so the Next.js frontend can call /chat/stream.
- Sessions are stored in-memory; scaling horizontally requires moving them to a shared store.

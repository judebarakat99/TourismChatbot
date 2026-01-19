# TourismChatbot API Reference

## FastAPI auto-docs
- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc
Both reflect the live OpenAPI schema generated from `app.main`.

## Authentication
No authentication is enforced yet. Restrict access at the network layer (VPN, private VNet, API gateway) before exposing the service publicly.

## Endpoints
### `GET /health`
Returns a JSON heartbeat payload.
```json
{
  "status": "healthy",
  "service": "Tourism Chatbot API",
  "rag_enabled": true
}
```

### `POST /chat/stream`
Streams chat completions via Server-Sent Events.
- **Body**
  ```json
  {
    "message": "Two-day itinerary in Florence",
    "session_id": "user-123",
    "language": "en"
  }
  ```
- **Events**
  - `event: token` → incremental completion tokens (JSON-encoded strings)
  - `event: meta` → emitted once with `{ "topic": "Italy Tourism", "message": "Response completed using trained RAG system" }`
  - `event: error` → sent if an exception bubbles up
- **Example**
  ```bash
  curl -N \
    -H "Content-Type: application/json" \
    -d '{"message":"Best time to visit Rome?","session_id":"demo","language":"en"}' \
    http://localhost:8000/chat/stream
  ```
  Use the `-N`/`--no-buffer` flag so curl prints each SSE event as it arrives.

### `GET /chat`
Legacy streaming endpoint that accepts `question` and optional `language` query parameters and streams raw tokens (`data: ...`). Prefer `/chat/stream`, which includes session management and structured events.

### `DELETE /conversations/{conversation_id}`
Removes an in-memory conversation. Returns `{ "success": true }` even if the ID does not exist.

## Error handling
- Validation errors return HTTP 422 with FastAPI's standard schema.
- Runtime errors during streaming result in an `event: error` SSE followed by connection close; check the backend logs for stack traces.
- Qdrant connectivity issues propagate as HTTP 500 responses during startup because the vector store is instantiated when importing `app.qdrant.retrieval`.

## Versioning & change tips
- Bump `AZURE_OPENAI_*` variables to test new deployments without code changes.
- If you add new endpoints, they appear automatically in `/docs` and `/redoc`; regenerating client SDKs is as simple as downloading the OpenAPI JSON from `/openapi.json`.

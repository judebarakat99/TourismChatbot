# TourismChatbot User Guide

## Before you start
1. Start Qdrant, the FastAPI backend, and the Next.js frontend (see the root [README.md](../README.md) or [docs/OPERATIONS.md](OPERATIONS.md) for exact commands).
2. Visit http://localhost:3000 — the status banner above the input shows whether the backend `/health` endpoint is reachable.

## Starting a conversation
1. Click **New Chat** in the left sidebar to generate a fresh session with its own `session_id`.
2. Use the prompt buttons on the empty state ("Top destinations", "Plan my trip", etc.) or type your own question in the composer at the bottom.
3. Submit with **Send** (or press Enter). While a reply streams in, the button shows `⏳` and the input is disabled.
4. Assistant replies render token-by-token; you can scroll or wait for the message to finish. Any supporting tags (for example the travel topic) appear under each assistant bubble.
5. When the backend includes citations in the SSE `meta` payload, they show up under **📌 Sources** for that answer.

## Managing conversations
- **Recent chats:** The sidebar keeps the six most recent conversations. Click one to resume the associated session context.
- **Favorites:** Toggle the star icon to pin itineraries you revisit often. Favorites appear in their own list above the recents.
- **Deleting:** Use the `✕` icon to remove a populated conversation. Empty chats stay in place so you always have an active pane.
- **Session continuity:** Each conversation holds its own UUID `sessionId`, so follow-up questions stay grounded in earlier answers until you create a new chat.

## Switching languages
- Use the globe/language selector in the header (Settings → Language) to flip between English (`en`) and Arabic (`ar`).
- The UI automatically switches to RTL layout for Arabic and persists your choice in `localStorage`.
- The frontend sends the selected language to the backend (`language` field in `/chat/stream`), so responses arrive localized as long as the underlying model supports it.

## Troubleshooting tips
- **Backend unavailable banner:** Hover the warning above the composer and open http://localhost:8000/health in a new tab to confirm the API is up.
- **Stuck loading:** Open your browser dev tools → Network → `chat/stream` to ensure SSE events are arriving. A 401/500 usually means missing Azure credentials.
- **Empty answers:** Check the backend terminal for `Error in stream_answer` logs; re-run ingestion if no documents were found at startup.

Need more detail? See the developer docs in [docs/API.md](API.md) and [docs/environment/ENVIRONMENT_GUIDE.md](environment/ENVIRONMENT_GUIDE.md).

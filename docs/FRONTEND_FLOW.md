# Frontend Flow Guide

The Routey UI (Next.js + React) guides users through session creation, streaming chat, and language-aware rendering. The flow below focuses on src/app/page.tsx and supporting libs.

## User Interaction Flowchart
```text
[Page mount]
        |
        v
[Init default conversation + sessionId]
        |
        v
[Load saved language + fire healthCheck()]
        |
        v
[User types message or clicks recommendation]
        |
        v
[Append user + placeholder assistant message in state]
        |
        v
[call chatWithStream({message, session_id, language})]
        |
        v
[Fetch returns ReadableStream -> reader loop starts]
        |
        v
[Decode SSE events: token vs meta]
        |
        v
[token events append to assistant content]
        |
        v
[meta events capture optional source metadata]
        |
        v
[State updates trigger UI render + auto-scroll]
        |
        v
[Stream ends -> setIsLoading(false)]
```

## Sidebar + Session Management
```text
[New Chat click] -> [Create conversation w/ fresh sessionId]
[Delete Chat] -> [If messages exist, drop convo + open new empty one]
[Favorite toggle] -> [Flip isFavorite flag in state]
[Language change] -> [Persist in localStorage + switch RTL/LTR]
```

## Step Notes
- chatWithStream() and healthCheck() live in frontend/src/lib/api.ts.
- Language strings (EN, AR) come from frontend/src/lib/translations.ts and drive placeholders + layout direction.
- Streaming loop buffers partial SSE chunks, ensuring incomplete events remain in `buffer` until finished.
- Messages keep `sources` so future UI can display citations emitted via `event: meta`.
- CSS + typography defaults are defined in frontend/src/app/globals.css and applied through RootLayout.

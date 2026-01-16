# How to Connect Backend to Frontend - Step by Step

## Setup First

### Step 1: Set the Backend URL
In the frontend folder, create a file called `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This tells the frontend where to find the backend. 
- For local development: `http://localhost:8000`
- For production: your actual server URL

### Step 2: Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

Frontend runs on: `http://localhost:3000`

---

## What the Frontend Expects from Backend

The frontend calls the backend with 2 endpoints. Here's exactly what it does.

---

## Endpoint 1: Chat Stream (Most Important)

### Where It's Called From
File: `frontend/src/app/page.tsx`  
Function: `handleSubmit()` around line 292

### How Frontend Calls It
```javascript
const response = await fetch(`${API_BASE}/chat/stream`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "Tell me about Rome",
    session_id: "user-session-123",
    language: "en"
  })
});
```

**Variables:**
- `API_BASE` = `http://localhost:8000` (from .env.local)
- `message` = what user typed in the chat box
- `session_id` = unique ID for this conversation
- `language` = "en" (English) or "ar" (Arabic)

### What Your Backend Should Implement

**Endpoint URL:** `POST http://localhost:8000/chat/stream`

**Accept this request body:**
```json
{
  "message": "Tell me about Rome",
  "session_id": "user-session-123",
  "language": "en"
}
```

**Send back streaming response** in Server-Sent Events (SSE) format.

Frontend receives chunks one at a time. Each chunk starts with `data: ` followed by JSON.

**Example response chunks:**

Chunk 1:
```
data: {"type":"content","content":"Rome is"}
```

Chunk 2:
```
data: {"type":"content","content":" the capital"}
```

Chunk 3:
```
data: {"type":"content","content":" of Italy"}
```

Final chunk:
```
data: {"type":"complete","topic":"Italy Attractions","sources":[{"title":"Wikipedia","source":"Rome"},{"title":"Travel Guide","source":"Italian Tourism"}]}
```

**Important:** Each chunk must be on a separate line and end with a newline (`\n`).

### Response Format Details

**"content" events:**
- `type: "content"` = piece of text to display
- `content: "..."` = the actual text
- These come multiple times as response is generated

**"complete" event:**
- `type: "complete"` = final event (comes once at end)
- `topic: "..."` = category/subject of the response
- `sources: [...]` = list of where information came from

**Sources array:**
Each source is an object:
```json
{
  "title": "Wikipedia",
  "source": "Rome Attractions"
}
```

### How Frontend Handles It

Frontend code in `page.tsx` lines 350-390:

1. Receives response stream
2. Reads chunks as they arrive
3. Finds lines starting with `data: `
4. Parses the JSON
5. If `type: "content"` → adds text to message on screen in real-time
6. If `type: "complete"` → stops streaming, shows final topic and sources
7. Saves conversation to browser storage

---

## Endpoint 2: Delete Conversation

### Where It's Called From
File: `frontend/src/app/page.tsx`  
Function: `deleteConversation()` around line 308

### How Frontend Calls It
```javascript
const response = await fetch(
  `${API_BASE}/conversations/${conversationId}`,
  {
    method: 'DELETE',
  }
);

if (!response.ok) {
  throw new Error('Failed to delete conversation');
}
```

**Variables:**
- `API_BASE` = `http://localhost:8000`
- `conversationId` = ID of the conversation (example: `conv-1704067200000`)

### What Your Backend Should Implement

**Endpoint URL:** `DELETE http://localhost:8000/conversations/{id}`

**Example request:**
```
DELETE /conversations/conv-1704067200000
```

**Expected response:**
- Status code: `200 OK`
- Body: empty or `{"success": true}`

**What frontend expects:**
- Status 200 = success ✓ (shows success message)
- Any other status = error ✗ (shows error message)

---

## Testing the Integration

### Test 1: Chat Stream

Open your terminal and run:

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Venice",
    "session_id": "test-123",
    "language": "en"
  }'
```

**You should see output like:**
```
data: {"type":"content","content":"Venice is"}
data: {"type":"content","content":" a city"}
data: {"type":"content","content":" in Italy"}
data: {"type":"complete","topic":"Italy Attractions","sources":[{"title":"Wikipedia","source":"Venice"}]}
```

If you see this, it's working!

### Test 2: Delete Conversation

```bash
curl -X DELETE http://localhost:8000/conversations/conv-123
```

**You should see:**
- No error
- Status 200

---

## Common Issues

### Issue 1: 404 Not Found
**What it means:** Backend endpoint doesn't exist

**Solution:** Check that your backend has these routes:
- `POST /chat/stream` (note: exact spelling and case)
- `DELETE /conversations/{id}`

### Issue 2: CORS Error in Browser (Red text in browser console)
**What it means:** Browser blocks request because backend doesn't allow it

**Solution:** Add CORS to your backend. Example for FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Stream not showing in chat
**What it means:** Frontend receives response but can't parse it

**Solutions:**
1. Check format: each data chunk must start with `data: ` (note the space after)
2. Check JSON: each JSON must be valid (no syntax errors)
3. Check line breaks: each chunk must be on separate line with `\n`

### Issue 4: .env.local not working
**What it means:** Frontend still using default localhost:8000

**Solution:**
1. Create `.env.local` in `frontend/` folder (not `frontend/src/`)
2. Restart: stop `npm run dev` and run it again
3. Verify: Open browser console and type `console.log(process.env.NEXT_PUBLIC_API_URL)`

---

## Before You Start: Checklist

Make sure you have:
- [ ] Node.js installed
- [ ] Frontend folder has `node_modules/` (run `npm install` if not)
- [ ] Backend running on port 8000
- [ ] `.env.local` file in frontend folder
- [ ] Backend endpoints responding to requests

---

## Quick Integration Test

1. **Terminal 1: Start frontend**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Terminal 2: Start backend**
   ```bash
   # Whatever command starts your backend
   # (python main.py, uvicorn app.main:app, etc.)
   ```

3. **Browser:**
   - Go to http://localhost:3000
   - Type: "Tell me about Rome"
   - Click Send
   - Should see AI response streaming in chat

If you see this, everything is connected!

---

## Line-by-Line Code Reference

### Frontend calls chat endpoint (page.tsx line 292):
```typescript
const request = {
  message: inputText,
  session_id: currentConversationId,
  language: language
};

const stream = await chatWithStream(request);
```

Where `chatWithStream()` is in `src/lib/api.ts`:
```typescript
export async function chatWithStream(request: ChatRequest): Promise<ReadableStream<Uint8Array>> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Chat request failed');
  }

  return response.body!;
}
```

### Frontend deletes conversation (page.tsx line 308):
```typescript
const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
  method: 'DELETE',
});

if (!response.ok) {
  throw new Error('Failed to delete');
}
```

---

## That's All You Need!

Just implement those 2 endpoints with the format shown above, and the frontend will work perfectly. If you get stuck, check the error messages in the browser console (press F12 to open developer tools).

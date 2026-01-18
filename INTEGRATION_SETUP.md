# Tourism Chatbot - Frontend & Backend Integration Status

## ✅ Completed Setup

### 1. Frontend Configuration
- **File**: `frontend/.env.local`
- **Content**: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Status**: ✅ Created and configured

### 2. Backend Endpoints Implemented

#### Endpoint 1: Health Check
- **URL**: `GET /health`
- **Purpose**: Frontend checks if backend is running
- **Response**: 
  ```json
  {
    "status": "healthy",
    "service": "Tourism Chatbot API"
  }
  ```

#### Endpoint 2: Chat Stream (MAIN ENDPOINT)
- **URL**: `POST /chat/stream`
- **Request Body**:
  ```json
  {
    "message": "Tell me about Rome",
    "session_id": "user-session-123",
    "language": "en"
  }
  ```
- **Response Format**: Server-Sent Events (SSE)
  - Streams content chunks: `data: {"type":"content","content":"text here"}`
  - Final completion: `data: {"type":"complete","topic":"Italy Tourism","sources":[]}`

#### Endpoint 3: Delete Conversation
- **URL**: `DELETE /conversations/{id}`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Conversation deleted"
  }
  ```

### 3. CORS Middleware
- **Status**: ✅ Added
- **Allowed Origins**: 
  - http://localhost:3000 (Frontend)
  - http://localhost:8000 (Backend)
- **Allowed Methods**: All (GET, POST, DELETE, etc.)
- **Allowed Headers**: All

## 🚀 Running the Application

### Option 1: Docker Compose (Recommended)
```bash
cd Tourism_Chatbot/TourismChatbot
docker-compose up
```
This will start:
- Qdrant (port 6333)
- Backend (port 8000)
- Frontend (port 3000)

### Option 2: Manual Start

**Terminal 1 - Qdrant:**
```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

**Terminal 2 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📋 Integration Checklist

- [x] Frontend `.env.local` configured
- [x] `POST /chat/stream` endpoint implemented
- [x] `DELETE /conversations/{id}` endpoint implemented
- [x] `GET /health` endpoint implemented
- [x] CORS middleware configured
- [x] SSE response format matches frontend expectations
- [x] Session management in backend

## 🧪 Testing Endpoints

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Chat Stream
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Venice",
    "session_id": "test-123",
    "language": "en"
  }'
```

Expected output:
```
data: {"type":"content","content":"Venice is"}
data: {"type":"content","content":" a city"}
data: {"type":"complete","topic":"Italy Tourism","sources":[]}
```

### Test 3: Delete Conversation
```bash
curl -X DELETE http://localhost:8000/conversations/conv-123
```

## 📱 Frontend & Backend Communication Flow

```
User enters message in Frontend (page.tsx)
        ↓
Frontend calls POST /chat/stream
        ↓
Backend receives request with message, session_id, language
        ↓
Backend queries RAG system for context
        ↓
Backend streams response in SSE format:
  - Content chunks: type: "content"
  - Final metadata: type: "complete"
        ↓
Frontend receives chunks in real-time
        ↓
Frontend displays message as it arrives (streaming effect)
        ↓
User sees AI response appear gradually in chat
```

## 🔧 Important Notes

1. **Environment Variables**: Backend uses `.env` file with Azure OpenAI credentials
2. **Session Management**: Each conversation has a unique session_id for history tracking
3. **Streaming**: Frontend expects SSE format with `data: ` prefix on each line
4. **Language Support**: Both "en" (English) and "ar" (Arabic) supported
5. **Error Handling**: Backend sends error type in SSE if something fails

## 📝 Files Modified/Created

- ✅ `frontend/.env.local` - Created
- ✅ `backend/app/main.py` - Updated with new endpoints
- ✅ `backend/.env` - Configured with Azure credentials

## ✨ Ready to Use!

The chatbot is now fully connected. When you run the application:
1. Frontend will check backend health on startup
2. Users can type messages and see AI responses streaming
3. Conversations can be managed (created, deleted)
4. Supports multiple languages
5. Session history is maintained for context

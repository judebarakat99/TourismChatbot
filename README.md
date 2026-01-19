# TourismChatbot

An intelligent Tourism Chat Bot Assistant that helps users discover tourism events, attractions, and activities using RAG (Retrieval-Augmented Generation) with Azure OpenAI and Qdrant vector database. Supports English and Arabic with real-time streaming responses.

## Features ✅

- **FastAPI Backend** with streaming chat endpoint (`/chat/stream`) using Server-Sent Events (SSE) 🔁
- **Next.js Frontend** with responsive UI, real-time streaming display, and multi-language support 🎨
- **Azure OpenAI Integration** for intelligent conversational responses 🤖
- **Qdrant Vector Database** for document similarity search and RAG context retrieval 🔎
- **Multi-Language Support** English and Arabic with RTL layout support 🌍
- **Document Ingestion Pipeline** for tourism knowledge base (88 indexed chunks) 📄
- **Session Management** with conversation history and multi-tab synchronization 💾

---

## Tech Stack

- **Backend**: Python, FastAPI, LangChain, Qdrant, Azure OpenAI
- **Frontend**: Next.js 16.1.1, TypeScript, React 19, Tailwind CSS
- **Database**: Qdrant (Vector DB)
- **LLM**: Azure OpenAI (gpt-5-chat)

---

## Quick Start (Development) 🚀

### Prerequisites

- Python 3.11+ 
- Node.js 18+
- Azure OpenAI API key
- Qdrant instance (Docker or local)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create `.env` file with Azure credentials:**
```env
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-5-chat
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
CORS_ORIGINS=*
APP_NAME=Tourism Bot API
```

3. **Create Python virtual environment (Optional but recommended):**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Start Qdrant (using Docker):**
```bash
docker-compose up -d
```

6. **Ingest tourism data into Qdrant:**
```bash
python scripts/ingest.py
```
This will automatically ingest all documents from `data/` folder (88 chunks) into the `tourism_docs` collection.

7. **Run the backend server:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

**API Documentation (Swagger UI):** `http://localhost:8000/docs`

**Health Check:**
```bash
curl http://localhost:8000/health
```

---

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Create `.env.local` file:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Install dependencies:**
```bash
npm install
```

4. **Run the frontend development server:**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Running Both Servers Together

**Option 1: Separate Terminals**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option 2: Concurrent Command (from root directory)**
```bash
# On macOS/Linux:
(cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) & (cd frontend && npm run dev)

# On Windows PowerShell:
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd frontend; npm run dev"
```

---

## Docker Compose (deploy)

The [deploy](deploy) folder now holds dedicated Compose files so you can start just the pieces you need or the full stack with explicit ordering.

### Single-service workflows

- [deploy/qdrant.compose](deploy/qdrant.compose): `docker compose -f deploy/qdrant.compose up -d` — launches Qdrant with persisted storage and a readiness probe.
- [deploy/backend.compose](deploy/backend.compose): `docker compose -f deploy/backend.compose up --build` — runs the FastAPI backend using your [backend/.env](backend/.env) file. By default it points `QDRANT_URL` at `http://host.docker.internal:6333`; override via `QDRANT_URL=...` if Qdrant lives elsewhere.
- [deploy/frontend.compose](deploy/frontend.compose): `docker compose -f deploy/frontend.compose up --build` — starts the Next.js dev server with hot reload. It targets `http://host.docker.internal:8000` unless you override `NEXT_PUBLIC_API_URL` when invoking Docker.

> Tip: launching Qdrant and backend via their dedicated Compose files keeps the containers isolated yet reachable through the published ports. When you need cross-container networking without host bridges, use the stack file below.

### Full stack with ordered boot

- [deploy/stack.compose](deploy/stack.compose): `docker compose -f deploy/stack.compose up --build` — spins up Qdrant → backend (after Qdrant healthcheck passes) → waits 30 seconds before starting the frontend so the API cache warms up. `depends_on` plus health checks guarantee Qdrant is online before the backend, and the frontend command adds the required 30-second pause after the backend becomes healthy.

All Compose files mount the local source directories, so code edits on the host reflect instantly inside the containers. Stop everything with `docker compose -f deploy/<file>.compose down` (add `-v` if you want to remove the named volumes like `qdrant_storage`).

---

## Project Structure 🏗️

```
TourismChatbot/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── langchain/
│   │   │   ├── rag.py             # RAG system
│   │   │   ├── chain.py           # LLM chain
│   │   │   └── prompts.py         # Custom prompts
│   │   ├── qdrant/
│   │   │   └── retrieval.py       # Vector DB retrieval
│   │   └── config/
│   │       └── settings.py        # Configuration
│   ├── data/                       # Tourism documents (88 chunks)
│   ├── scripts/
│   │   └── ingest.py              # Data ingestion script
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables
│   └── docker-compose.yml          # Qdrant Docker setup
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Home/Chat page
│   │   │   ├── settings/page.tsx  # Settings page
│   │   │   ├── account/page.tsx   # Account page
│   │   │   └── help/page.tsx      # Help/FAQ page
│   │   ├── hooks/
│   │   │   └── useLanguage.ts     # Language management hook
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   └── translations.ts   # i18n strings (EN/AR)
│   │   └── globals.css           # Tailwind styles
│   ├── package.json              # Node dependencies
│   ├── .env.local               # Environment variables
│   └── tsconfig.json            # TypeScript config
│
├── README.md
├── docker-compose.yml
└── requirements.txt (root)
```

---

## API Endpoints 📡

### Chat Streaming Endpoint
**POST** `/chat/stream`

Request:
```json
{
  "message": "What are the best attractions in Rome?",
  "session_id": "unique-session-id",
  "language": "en"
}
```

Response: Server-Sent Events (SSE) with tokens and sources

### Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "service": "Tourism Chatbot API",
  "rag_enabled": true
}
```

---

## Features & Usage 💡

### Chat Interface
- Send tourism-related questions
- View real-time streaming responses
- See sources and citations
- Manage conversation history
- Create and switch between conversations
- Favorite important conversations

### Language Support
- **English** (Default, LTR)
- **Arabic** (RTL layout)
- Language preference persists across sessions
- Synchronized across browser tabs

### Settings Page
- Change language preference
- Update notification settings
- Configure privacy options

### Account Management
- View and update profile
- Change password
- Delete account

### Help Section
- FAQ with expandable items
- Comprehensive help documentation

---

## Development 🔧

### Building Frontend for Production
```bash
cd frontend
npm run build
npm start
```

### Running Tests (Backend)
```bash
cd backend
pytest
```

### Linting & Formatting (Frontend)
```bash
cd frontend
npm run lint
npm run format
```

---

## Environment Variables Reference

### Backend `.env`
```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-5-chat

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# App Configuration
CORS_ORIGINS=*
APP_NAME=Tourism Bot API
```

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting 🔍

**Backend won't start:**
- Ensure Qdrant is running: `docker-compose up -d`
- Check Azure OpenAI credentials in `.env`
- Verify port 8000 is not in use

**Frontend won't connect to backend:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend is running on port 8000
- Check browser console for CORS errors

**Qdrant connection issues:**
- Verify Qdrant container is running: `docker ps`
- Check `QDRANT_URL` in backend `.env`
- Ensure port 6333 is accessible

**Data not ingesting:**
- Ensure documents are in `backend/data/` folder
- Run ingestion script: `python scripts/ingest.py`
- Check backend logs for ingestion status

---

## License & Contributing

Contributions welcome — open an issue or PR to contribute.

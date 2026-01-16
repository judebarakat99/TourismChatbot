from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os, json

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Tourism Bot API")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_uk")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatReq(BaseModel):
    message: str
    session_id: str
    language: str = "auto"

# Lazy-initialized globals (so app can boot even if env vars are wrong)
_vectorstore = None
_llm = None

def _ensure_ready():
    global _vectorstore, _llm

    missing = []
    if not AZURE_OPENAI_ENDPOINT: missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY: missing.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_CHAT_DEPLOYMENT: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")
    if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT: missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    if not QDRANT_URL: missing.append("QDRANT_URL")

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Backend misconfigured. Missing env vars: {', '.join(missing)}"
        )

    if _vectorstore is None or _llm is None:
        from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
        from qdrant_client import QdrantClient
        from langchain_community.vectorstores import Qdrant

        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )

        _llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
            temperature=0.2,
            streaming=True,
        )

        client = QdrantClient(url=QDRANT_URL)
        _vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embeddings)

    return _vectorstore, _llm


@app.get("/health")
def health():
    # Always respond even if config is wrong
    return {
        "status": "ok",
        "has_azure_openai": bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY),
        "has_qdrant_url": bool(QDRANT_URL),
        "qdrant_url": QDRANT_URL,
        "collection": QDRANT_COLLECTION,
    }


@app.post("/chat/stream")
async def chat_stream(req: ChatReq):
    vectorstore, llm = _ensure_ready()

    docs = vectorstore.similarity_search(req.message, k=5)
    context = "\n\n".join([d.page_content for d in docs])
    sources = [{"title": d.metadata.get("title", "source"), "source": d.metadata.get("source", "")} for d in docs]

    prompt = f"""
You are a UK tourism assistant.
Use the context to answer.
End with a Sources section.

Context:
{context}

Question:
{req.message}
"""

    async def gen():
        yield f"event: meta\ndata: {json.dumps({'sources': sources})}\n\n"
        async for chunk in llm.astream(prompt):
            if getattr(chunk, "content", None):
                safe = chunk.content.replace("\n", "\\n")
                yield f"event: token\ndata: {safe}\n\n"
        yield "event: done\ndata: done\n\n"

    return EventSourceResponse(gen())

from __future__ import annotations

import os
import json
import logging
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Optional imports (we will guard usage so the app can still boot)
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tourism-api")

APP_NAME = os.getenv("APP_NAME", "Tourism Bot API")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_uk")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

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

# ---- Lazy / guarded initialization so the app doesn't crash on boot ----
_llm: Optional[AzureChatOpenAI] = None
_vectorstore: Optional[Qdrant] = None

def init_llm() -> AzureChatOpenAI:
    global _llm
    if _llm is not None:
        return _llm

    missing = []
    if not AZURE_OPENAI_ENDPOINT: missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY: missing.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_CHAT_DEPLOYMENT: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if missing:
        raise RuntimeError(f"Missing Azure OpenAI env vars: {', '.join(missing)}")

    _llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
        temperature=0.2,
        streaming=True,
    )
    return _llm

def init_vectorstore() -> Optional[Qdrant]:
    """
    Return a Qdrant vector store if we can connect. If not, return None.
    """
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    # If env vars for embeddings are missing, we just skip RAG.
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_EMBEDDING_DEPLOYMENT):
        logger.warning("Embeddings env vars missing; running without Qdrant RAG.")
        return None

    try:
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )
        client = QdrantClient(url=QDRANT_URL)
        _vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embeddings)
        logger.info("Qdrant vectorstore initialized.")
        return _vectorstore
    except Exception as e:
        logger.exception("Could not initialize Qdrant; running without RAG. Error: %s", e)
        return None

@app.get("/health")
def health():
    # Always return OK so Azure Health Check can succeed.
    return {"status": "ok"}

@app.post("/chat/stream")
async def chat_stream(req: ChatReq):
    # Ensure LLM is configured. If not, return a clear error instead of crashing the whole app.
    try:
        llm = init_llm()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    vectorstore = init_vectorstore()

    sources: List[Dict[str, Any]] = []
    context = ""

    if vectorstore is not None:
        try:
            docs = vectorstore.similarity_search(req.message, k=5)
            context = "\n\n".join([d.page_content for d in docs])
            sources = [
                {"title": d.metadata.get("title", "source"), "source": d.metadata.get("source", "")}
                for d in docs
            ]
        except Exception as e:
            # Don't fail the request if Qdrant errors; just answer without context.
            logger.exception("Qdrant search failed; continuing without RAG. Error: %s", e)
            context = ""
            sources = []

    prompt = f"""
You are a UK tourism assistant.
Use the context to answer. If context is empty, answer normally.
End with a Sources section (even if empty).

Context:
{context}

Question:
{req.message}
""".strip()

    async def gen():
        # meta event first
        yield f"event: meta\ndata: {json.dumps({'sources': sources})}\n\n"

        async for chunk in llm.astream(prompt):
            if chunk.content:
                safe = chunk.content.replace("\n", "\\n")
                yield f"event: token\ndata: {safe}\n\n"

        yield "event: done\ndata: done\n\n"

    return EventSourceResponse(gen())

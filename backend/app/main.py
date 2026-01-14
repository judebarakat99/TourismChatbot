import os, json, logging
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv()

log = logging.getLogger("uvicorn.error")

APP_NAME = os.getenv("APP_NAME", "Tourism Bot API")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

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

_state = {
    "ready": False,
    "error": None,
    "vectorstore": None,
    "llm": None,
}

def _init_dependencies():
    # Lazy init so /health works even if deps are down/misconfigured
    if _state["ready"]:
        return

    missing = [k for k, v in {
        "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
        "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
        "AZURE_OPENAI_CHAT_DEPLOYMENT": AZURE_OPENAI_CHAT_DEPLOYMENT,
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        "QDRANT_URL": QDRANT_URL,
        "QDRANT_COLLECTION": QDRANT_COLLECTION,
    }.items() if not v]

    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
    from qdrant_client import QdrantClient
    from langchain_community.vectorstores import Qdrant

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    )

    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
        temperature=0.2,
        streaming=True,
    )

    client = QdrantClient(url=QDRANT_URL)
    vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embeddings)

    _state["llm"] = llm
    _state["vectorstore"] = vectorstore
    _state["ready"] = True
    _state["error"] = None

@app.get("/health")
def health():
    # Always respond so you can debug
    return {
        "status": "ok",
        "ready": _state["ready"],
        "qdrant_url": QDRANT_URL,
        "collection": QDRANT_COLLECTION,
        "error": _state["error"],
    }

@app.post("/chat/stream")
async def chat_stream(req: ChatReq):
    try:
        _init_dependencies()
    except Exception as e:
        _state["error"] = str(e)
        log.exception("Dependency init failed")
        raise HTTPException(status_code=500, detail=f"Startup/deps error: {e}")

    vectorstore = _state["vectorstore"]
    llm = _state["llm"]

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
            if chunk.content:
                safe = chunk.content.replace("\n", "\\n")
                yield f"event: token\ndata: {safe}\n\n"
        yield "event: done\ndata: done\n\n"

    return EventSourceResponse(gen())

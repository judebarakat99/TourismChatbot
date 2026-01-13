from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os, json

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Tourism Bot API")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_uk")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

if not AZURE_OPENAI_API_KEY:
    raise RuntimeError("Missing AZURE_OPENAI_API_KEY in .env")

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat/stream")
async def chat_stream(req: ChatReq):
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

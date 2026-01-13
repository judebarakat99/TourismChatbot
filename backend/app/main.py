from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os, asyncio, json
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant

load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME","Tourism Bot"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS","*").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatReq(BaseModel):
    message:str
    session_id:str
    language:str="auto"

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    temperature=0.2,
    streaming=True
)

client = QdrantClient(url=os.getenv("QDRANT_URL"))
vectorstore = Qdrant(
    client=client,
    collection_name=os.getenv("QDRANT_COLLECTION"),
    embeddings=embeddings
)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/chat/stream")
async def chat_stream(req:ChatReq):
    docs = vectorstore.similarity_search(req.message, k=5)
    context = "\n\n".join([d.page_content for d in docs])
    sources = [
        {"title":d.metadata.get("title"),"source":d.metadata.get("source")}
        for d in docs
    ]

    prompt = f"""
You are a UK tourism assistant.
Answer using the context.
Add a Sources section.

Context:
{context}

Question:
{req.message}
"""

    async def gen():
        yield f"event: meta\ndata: {json.dumps({'sources':sources})}\n\n"
        async for chunk in llm.astream(prompt):
            if chunk.content:
                yield f"event: token\ndata: {chunk.content}\n\n"
        yield "event: done\ndata: done\n\n"

    return EventSourceResponse(gen())

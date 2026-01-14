# app/qdrant/retrieval.py
import os
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from app.config.settings import QDRANT_URL, QDRANT_COLLECTION

# Initialize embeddings (same as ingest)
embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
)

# Connect to Qdrant collection
client = QdrantClient(url=QDRANT_URL)
vectorstore = QdrantVectorStore(
    client=client,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings
)

def retrieve_context(query: str, top_k: int = 3) -> str:
    """Return concatenated top-k retrieved documents as context."""
    docs = vectorstore.similarity_search(query, k=top_k)
    return "\n".join([doc.page_content for doc in docs])

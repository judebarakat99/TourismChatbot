# app/qdrant/retrieval.py
import os
from pathlib import Path
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config.settings import QDRANT_URL, QDRANT_COLLECTION

# ---- Config ----
DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[2] / "data"))
AUTO_INGEST = os.getenv("AUTO_INGEST", "false").lower() == "true"
EXPECTED_SIZE = 1536  # Adjust if your embedding deployment uses a different dimension

# ---- Embeddings & Client (initialized once) ----
embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION"),
)
client = QdrantClient(url=QDRANT_URL)

# ---- Helpers ----
def _collection_exists(name: str) -> bool:
    try:
        client.get_collection(name)
        return True
    except Exception:
        return False

def _create_collection(name: str, size: int = EXPECTED_SIZE) -> None:
    client.recreate_collection(
        collection_name=name,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )

def _load_txt_documents(root: str) -> List[Document]:
    """
    Recursively load .txt files under DATA_DIR as LangChain Documents.
    Metadata includes relative path for traceability.
    """
    docs: List[Document] = []
    root_path = Path(root)
    for path in root_path.rglob("*.txt"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = str(path.relative_to(root_path))
            docs.append(Document(page_content=text, metadata={"path": rel}))
        except Exception:
            # Skip unreadable files but continue
            continue
    return docs

def _chunks_from_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    # Ensure metadata is preserved
    for chunk in chunks:
        if "path" not in chunk.metadata:
            chunk.metadata["path"] = "unknown"
    return chunks


def _collection_is_empty(vs: QdrantVectorStore) -> bool:
    # Fast, approximate check: if a similarity search returns nothing, assume empty
    try:
        res = vs.similarity_search("healthcheck", k=1)
        return len(res) == 0
    except Exception:
        # If search fails, treat as empty to trigger ingestion
        return True

def _ingest_folder_if_needed(vs: QdrantVectorStore) -> None:
    if not AUTO_INGEST:
        return
    if _collection_is_empty(vs):
        docs = _load_txt_documents(DATA_DIR)
        if not docs:
            print(f"⚠ No .txt files found under DATA_DIR: {DATA_DIR}. Skipping ingestion.")
            return
        chunks = _chunks_from_docs(docs)
        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_URL,
            collection_name=QDRANT_COLLECTION,
        )
        print(f"✅ Ingested {len(chunks)} chunks from '{DATA_DIR}' into '{QDRANT_COLLECTION}'.")


# ---- Ensure collection & build vectorstore at import (safe) ----
if not _collection_exists(QDRANT_COLLECTION):
    print(f"ℹ Creating collection '{QDRANT_COLLECTION}'...")
    _create_collection(QDRANT_COLLECTION, size=EXPECTED_SIZE)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings,
)

# ---- Reset and ingest all files on startup if AUTO_INGEST is True ----
if AUTO_INGEST:
    print("Resetting collection and ingesting all files...")
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=EXPECTED_SIZE, distance=Distance.COSINE),
    )

    docs = _load_txt_documents(DATA_DIR)
    print(f"Found {len(docs)} documents in {DATA_DIR}")

    if docs:
        chunks = _chunks_from_docs(docs)
        print(f"Created {len(chunks)} chunks from documents")

        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_URL,
            collection_name=QDRANT_COLLECTION,
        )

        print(f"Ingested {len(chunks)} chunks from '{DATA_DIR}' into '{QDRANT_COLLECTION}'.")
    else:
        print("No documents found. Nothing ingested.")

# ---- Public API ----
def retrieve_context(query: str, top_k: int = 3) -> str:
    docs = vectorstore.similarity_search(query, k=top_k)
    context_parts = []
    for d in docs:
        source = d.metadata.get("path", "unknown")
        context_parts.append(f"[Source: {source}]\n{d.page_content}")
    return "\n".join(context_parts)

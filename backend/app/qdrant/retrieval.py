# app/qdrant/retrieval.py
import os
from pathlib import Path
from typing import List, Tuple
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config.settings import QDRANT_URL, QDRANT_COLLECTION

# ---- Config ----
DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[2] / "data"))
EXPECTED_SIZE = int(os.getenv("EMBEDDING_DIMENSION", "1536"))  # must match your embedding deployment

# ---- Embeddings & Client ----
embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)
client = QdrantClient(url=QDRANT_URL)

# ---- Collection lifecycle ----
def ensure_collection(name: str, size: int = EXPECTED_SIZE) -> None:
    """Create the collection if it doesn't exist."""
    try:
        client.get_collection(name)
        # exists → nothing to do
    except Exception:
        print(f"ℹ Creating collection '{name}' (size={size}, distance=COSINE)...")
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )

# ---- Data loading & chunking ----
def _load_txt_documents(root: str) -> List[Document]:
    """
    Recursively load .txt files under root as LangChain Documents.
    Stores relative file path in metadata['path'].
    """
    docs: List[Document] = []
    root_path = Path(root)
    for path in root_path.rglob("*.txt"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = str(path.relative_to(root_path))
            docs.append(Document(page_content=text, metadata={"path": rel}))
        except Exception:
            # skip unreadable files but continue
            continue
    return docs

def _chunks_from_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    for c in chunks:
        c.metadata.setdefault("path", "unknown")
    return chunks

def _make_ids(chunks: List[Document]) -> List[str]:
    """
    Stable, deterministic IDs so re-ingestion upserts rather than duplicates.
    Format: "<relative_path>#<chunk_index>"
    """    
    ids: List[str] = []
    counters: dict[str, int] = {}
    for c in chunks:
        rel = c.metadata.get("path", "unknown")
        idx = counters.get(rel, 0)
        counters[rel] = idx + 1
        ids.append(f"{rel}#{idx}")
    return ids

# ---- Ensure collection and build vectorstore ----
ensure_collection(QDRANT_COLLECTION, size=EXPECTED_SIZE)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings,
)

# ---- Always ingest all .txt files under DATA_DIR ----
docs = _load_txt_documents(DATA_DIR)
print(f"Found {len(docs)} documents in {DATA_DIR}")

if docs:
    chunks = _chunks_from_docs(docs)

    ids = [str(uuid.uuid4()) for _ in chunks]
    print(f"Prepared {len(chunks)} chunks. Ingesting (upsert by stable IDs)...")

    # Upsert chunks using deterministic IDs to avoid duplicates on repeated starts.
    vectorstore.add_documents(documents=chunks, ids=ids)

    print(f"✅ Ingested {len(chunks)} chunks into '{QDRANT_COLLECTION}'.")
else:
    print("No .txt documents found. Nothing ingested.")

# ---- Public API ----
def retrieve_context(query: str, top_k: int = 3) -> str:
    docs = vectorstore.similarity_search(query, k=top_k)
    context_parts = []
    for d in docs:
        source = d.metadata.get("path", "unknown")
        context_parts.append(f"[Source: {source}]\n{d.page_content}")
    return "\n".join(context_parts)

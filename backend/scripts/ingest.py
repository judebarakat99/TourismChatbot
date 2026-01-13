from pathlib import Path
import uuid, argparse, os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_community.vectorstores import Qdrant
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_uk")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

if not AZURE_OPENAI_API_KEY:
    raise RuntimeError("Missing AZURE_OPENAI_API_KEY in .env")

def main(path: str):
    docs = []
    for p in Path(path).rglob("*.md"):
        docs.append(
            Document(
                page_content=p.read_text(encoding="utf-8", errors="ignore"),
                metadata={"title": p.stem, "source": str(p)},
            )
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    )

    client = QdrantClient(url=QDRANT_URL)
    vec = embeddings.embed_query("test")

    client.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=len(vec), distance=Distance.COSINE),
    )

    vs = Qdrant(client, QDRANT_COLLECTION, embeddings)
    vs.add_documents(chunks, ids=[str(uuid.uuid4()) for _ in chunks])
    print(f"Ingested {len(chunks)} chunks into {QDRANT_COLLECTION}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    args = ap.parse_args()
    main(args.path)


import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import QDRANT_URL, QDRANT_COLLECTION

# 1) Initialize Azure OpenAI embeddings (your config)
embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"), 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
)

print(len(embeddings.embed_query("Hello from Jordan"))) ##############

# 2) Connect to Qdrant
client = QdrantClient(url=QDRANT_URL)

# 3) Ensure collection exists with correct size
EXPECTED_SIZE = 1536  # For text-embedding-3-small

try:
    info = client.get_collection(QDRANT_COLLECTION)
    # Depending on qdrant-client version, this path may differ.
    # Try safe extraction of size:
    current_size = None
    try:
        current_size = info.config.params.vectors.size
    except Exception:
        try:
            # Newer multi-vector schema may store as a dict
            current_size = list(info.config.params.vectors.values())[0].size
        except Exception:
            pass

    if current_size != EXPECTED_SIZE:
        print(f"⚠ Collection '{QDRANT_COLLECTION}' has size {current_size}, expected {EXPECTED_SIZE}. Recreating...")
        client.delete_collection(QDRANT_COLLECTION)
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EXPECTED_SIZE, distance=Distance.COSINE)
        )
        print(f"✅ Recreated collection '{QDRANT_COLLECTION}' with size {EXPECTED_SIZE}.")
    else:
        print(f"✅ Collection '{QDRANT_COLLECTION}' already exists with correct size ({current_size}).")
except Exception:
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=EXPECTED_SIZE, distance=Distance.COSINE)
    )
    print(f"✅ Created collection '{QDRANT_COLLECTION}' with size {EXPECTED_SIZE}.")

# 4) Test embeddings before ingestion
try:
    test_vector = embeddings.embed_query("Hello from Jordan")
    print(f"✅ Embedding test successful. Dimension: {len(test_vector)} (expected {EXPECTED_SIZE})")
except Exception as e:
    raise RuntimeError(f"Embedding test failed: {e}")

# 5) Sample tourism data (replace with real data later)
def load_raw_items() -> List[Dict]:
    return [
        {
            "page_content": "Jerash Festival is a major summer cultural event in Jordan featuring music and performances.",
            "metadata": {
                "country": "Jordan",
                "city": "Jerash",
                "type": "festival",
                "name": "Jerash Festival",
                "season": "summer",
                "language": "en",
                "source_url": "https://example.com/jerash",
                "date_start": "2026-07-01",
                "date_end": "2026-07-15"
            },
        },
        {
            "page_content": "Petra is a UNESCO World Heritage Site and one of Jordan's most famous landmarks.",
            "metadata": {
                "country": "Jordan",
                "city": "Petra",
                "type": "landmark",
                "name": "Petra",
                "language": "en",
                "source_url": "https://example.com/petra"
            },
        }
    ]

def to_documents(items: List[Dict]) -> List[Document]:
    return [Document(page_content=i["page_content"], metadata=i["metadata"]) for i in items]

# 6) Ingest into Qdrant
def ingest():
    raw_items = load_raw_items()
    docs = to_documents(raw_items)

    # Split into chunks for better retrieval
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    # Upsert into Qdrant
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION
    )
    print(f"✅ Ingested {len(chunks)} chunks into '{QDRANT_COLLECTION}'.")

if __name__ == "__main__":
    ingest()

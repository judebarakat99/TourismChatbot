#!/usr/bin/env python3
"""
Ingest training data from text files into Qdrant vector database.
Run this script to populate the Qdrant database with tourism training documents.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_openai import AzureOpenAIEmbeddings

# Configuration
DATA_DIR = Path(__file__).parent / "data"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_docs")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def load_documents_from_files() -> list[Document]:
    """Load all .txt files from the data directory as Documents."""
    documents = []
    
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        return documents
    
    txt_files = list(DATA_DIR.glob("*.txt"))
    print(f"📂 Found {len(txt_files)} text files in {DATA_DIR}")
    
    for file_path in txt_files:
        print(f"  📄 Loading {file_path.name}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path.name,
                        "path": str(file_path),
                        "type": "tourism_guide"
                    }
                )
                documents.append(doc)
        except Exception as e:
            print(f"    ❌ Error loading {file_path.name}: {e}")
    
    print(f"✅ Loaded {len(documents)} documents")
    return documents

def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into smaller chunks for better retrieval."""
    print(f"\n🔪 Chunking documents (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks

def initialize_embeddings():
    """Initialize Azure OpenAI embeddings."""
    print("\n🔐 Initializing Azure OpenAI embeddings...")
    
    embeddings = AzureOpenAIEmbeddings(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
    )
    
    # Test embedding
    try:
        test_vector = embeddings.embed_query("test")
        print(f"✅ Embeddings initialized (dimension: {len(test_vector)})")
        return embeddings
    except Exception as e:
        print(f"❌ Failed to initialize embeddings: {e}")
        raise

def initialize_qdrant():
    """Initialize Qdrant client and ensure collection exists."""
    print(f"\n🔷 Initializing Qdrant at {QDRANT_URL}...")
    
    client = QdrantClient(url=QDRANT_URL)
    
    # Check if collection exists
    try:
        collection_info = client.get_collection(QDRANT_COLLECTION)
        print(f"✅ Collection '{QDRANT_COLLECTION}' exists")
        # Delete and recreate to ensure clean state
        print(f"  🗑️  Recreating collection for fresh ingestion...")
        client.delete_collection(QDRANT_COLLECTION)
    except:
        pass
    
    # Create collection with proper vector dimensions (1536 for text-embedding-3-small)
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    print(f"✅ Collection '{QDRANT_COLLECTION}' ready")
    return client

def ingest_to_qdrant(chunks: list[Document], embeddings, client):
    """Ingest chunked documents into Qdrant."""
    print(f"\n⬆️  Ingesting {len(chunks)} chunks into Qdrant...")
    
    try:
        # Use LangChain's QdrantVectorStore for clean integration
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_URL,
            collection_name=QDRANT_COLLECTION,
        )
        print(f"✅ Successfully ingested {len(chunks)} chunks into Qdrant")
        return vector_store
    except Exception as e:
        print(f"❌ Failed to ingest into Qdrant: {e}")
        raise

def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("🚀 Tourism Chatbot Training Data Ingestion")
    print("=" * 60)
    
    try:
        # Load documents
        documents = load_documents_from_files()
        if not documents:
            print("\n❌ No documents to ingest!")
            return False
        
        # Chunk documents
        chunks = chunk_documents(documents)
        
        # Initialize embeddings
        embeddings = initialize_embeddings()
        
        # Initialize Qdrant
        client = initialize_qdrant()
        
        # Ingest to Qdrant
        ingest_to_qdrant(chunks, embeddings, client)
        
        print("\n" + "=" * 60)
        print("✅ Ingestion completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  • Documents loaded: {len(documents)}")
        print(f"  • Chunks created: {len(chunks)}")
        print(f"  • Collection: {QDRANT_COLLECTION}")
        print(f"  • Qdrant URL: {QDRANT_URL}")
        print("\n🎉 Ready to use with the chatbot!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

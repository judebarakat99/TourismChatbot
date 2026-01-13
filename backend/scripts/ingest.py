from pathlib import Path
import uuid, argparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_community.vectorstores import Qdrant
from dotenv import load_dotenv
import os
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

def main(path):
    docs=[]
    for p in Path(path).rglob("*.md"):
        docs.append(Document(
            page_content=p.read_text(encoding="utf-8"),
            metadata={"title":p.stem,"source":str(p)}
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )

    client = QdrantClient(url=os.getenv("QDRANT_URL"))
    vec = embeddings.embed_query("test")

    client.recreate_collection(
        collection_name=os.getenv("QDRANT_COLLECTION"),
        vectors_config=VectorParams(size=len(vec), distance=Distance.COSINE)
    )

    vs = Qdrant(client, os.getenv("QDRANT_COLLECTION"), embeddings)
    vs.add_documents(chunks, ids=[str(uuid.uuid4()) for _ in chunks])
    print("Ingested",len(chunks),"chunks")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--path",required=True)
    args=ap.parse_args()
    main(args.path)

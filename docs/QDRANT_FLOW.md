# Qdrant Data Flow Guide

The diagrams below describe how the vector database layer is initialized, populated, and queried inside the Tourism Chatbot stack.

## Ingestion Flow (from raw tourism docs to Qdrant)
```text
[Start / Service Boot]
        |
        v
[Load env vars + defaults]
        |
        v
[Initialize Azure OpenAI embeddings]
        |
        v
[Connect to Qdrant & ensure collection schema]
        |
        v
[Scan DATA_DIR for .txt content]
        |
        v
[Convert files -> LangChain Documents]
        |
        v
[Chunk Documents w/ Recursive splitter]
        |
        v
[Generate deterministic IDs per chunk]
        |
        v
[Embed + upsert chunks via QdrantVectorStore]
        |
        v
[Log status + ready for retrieval]
```

## Retrieval Flow (serving context to the RAG chain)
```text
[Inferred user question]
        |
        v
[Azure embeddings encode query]
        |
        v
[Build vector search request (top_k)]
        |
        v
[Qdrant similarity search over collection]
        |
        v
[Collect best-matching chunks + metadata]
        |
        v
[Decorate snippets w/ source path tags]
        |
        v
[Join snippets into context string]
        |
        v
[Return context to LangChain prompt]
```

## Step Notes
- Initialization, collection checks, and ingest logic live in backend/app/qdrant/ingest.py.
- Runtime retrieval, DATA_DIR scanning, and deterministic chunk IDs live in backend/app/qdrant/retrieval.py.
- EXPECTED_SIZE (1536) must stay aligned with the active Azure embedding deployment (text-embedding-3-small).
- Chunking defaults (size 1000 / overlap 150) match CHUNK_SIZE and CHUNK_OVERLAP in backend/app/config/settings.py.
- Source tags added during retrieval allow the LLM prompt to cite documents as Source:[name].

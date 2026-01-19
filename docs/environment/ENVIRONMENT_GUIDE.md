# Environment Configuration Templates

Use the files in this directory to bootstrap local or cloud deployments.

## Files
- [.env.example](.env.example) — drop-in template for `backend/.env`
- [requirements.txt](requirements.txt) — minimal dependency set if you need to recreate the backend environment outside this repo

## Setup steps
1. Copy `.env.example` into `backend/.env`.
2. Replace every `replace-with-...` placeholder with the values from your Azure OpenAI resources and Qdrant instance.
3. Update `DATA_DIR` if you keep documents outside `backend/data`.
4. (Optional) Install Python dependencies in a clean virtual environment with:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r docs/environment/requirements.txt
   ```
   Then install the project dependencies with `pip install -r backend/requirements.txt` to stay fully aligned.

## Key variables
| Name | Purpose | Example |
| --- | --- | --- |
| `AZURE_OPENAI_API_KEY` | API key for the chat deployment | `xxxxxxxxxxxxxxxxxx` |
| `AZURE_OPENAI_ENDPOINT_CHAT` | Base URL for the chat Azure OpenAI resource | `https://my-chat.openai.azure.com/` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Name of the deployed chat model | `gpt-5-chat` |
| `AZURE_OPENAI_CHAT_API_VERSION` | API version used by LangChain when calling the chat deployment | `2024-12-01-preview` |
| `AZURE_OPENAI_EMBEDDING_KEY` | API key for the embedding resource (often the same as chat if shared) | `xxxxxxxxxxxxxxxxxx` |
| `AZURE_OPENAI_ENDPOINT` | Endpoint for embeddings | `https://my-embeddings.openai.azure.com/` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Name of the embedding deployment | `text-embedding-3-small` |
| `AZURE_OPENAI_EMBEDDING_API_VERSION` | API version for embeddings | `2024-02-01` |
| `QDRANT_URL` | Public URL of your Qdrant instance | `http://localhost:6333` |
| `QDRANT_COLLECTION` | Collection name that stores tourism vectors | `tourism_docs` |
| `DATA_DIR` | Absolute path to the Markdown/TXT corpus | `C:/path/to/backend/data/italy` |
| `AUTO_INGEST` | If `true`, load documents on startup | `true` |
| `RETRIEVAL_TOP_K` | Number of chunks fetched per query | `5` |
| `CHUNK_SIZE` | Characters per chunk when splitting | `1000` |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks | `200` |
| `EMBEDDING_DIMENSION` | Vector size expected by Qdrant | `1536` |

## Tips
- Keep `.env` files out of version control; `.env.example` is the only committed template.
- When deploying to Azure Container Apps or App Service, convert these keys into platform secrets and inject them as environment variables.
- Run `python backend/azure_diagnostic.py` after editing `.env` to verify credentials before starting the API.

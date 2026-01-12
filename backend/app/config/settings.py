
# backend/app/config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Azure OpenAI settings
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Qdrant settings
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "tourism_docs")

# Default app settings
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "Jordan")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

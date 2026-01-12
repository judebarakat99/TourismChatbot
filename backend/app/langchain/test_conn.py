from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Initialize LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.3,
    streaming=True,  # streaming must be True for stream()
    openai_api_version=os.getenv("OPENAI_API_VERSION"),
)

# Test streaming
try:
    print("✅ Streaming response:")
    for chunk in llm.stream([{"role": "user", "content": "Hello"}]):
        # chunk is a dict, text is in 'delta'
        if 'content' in chunk:
            print(chunk['content'], end='', flush=True)
        elif 'delta' in chunk:
            print(chunk['delta'], end='', flush=True)
    print("\n✅ Done!")
except Exception as e:
    print("❌ Something went wrong:")
    print(e)

# backend/app/langchain/chain.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from app.langchain.prompts import prompt

# Load .env
load_dotenv()

# Initialize Azure Chat LLM
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_CHAT_API_VERSION")

print(f"DEBUG: Using endpoint: {endpoint}")
print(f"DEBUG: Using deployment: {deployment}")
print(f"DEBUG: API key set: {bool(api_key)}")

llm = AzureChatOpenAI(
    azure_deployment=deployment,  
    temperature=0.3,
    streaming=True,
    openai_api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

# Create chain
chain = prompt | llm


def stream_answer(
    question: str,
    context: str,
    chat_history: str,
    current_date: str,
    language: str = "en"
):
    """
    Render the prompt with the input variables and stream the LLM response.
    """
    try:
        # Use the chain to process the input and stream the output
        input_data = {
            "question": question,
            "context": context,
            "chat_history": chat_history,
            "current_date": current_date,
            "language": language
        }
        
        # Stream output from the chain
        for chunk in chain.stream(input_data):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    except Exception as e:
        print(f"Error in stream_answer: {str(e)}")
        yield ""

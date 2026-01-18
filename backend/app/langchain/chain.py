# backend/app/langchain/chain.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from app.langchain.prompts import prompt

# Load .env
load_dotenv()

# Initialize Azure Chat LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),  
    temperature=0.3,
    streaming=True,
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
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
    # Format messages with keywords
    messages = prompt.format_messages(
        question=question,
        context=context,
        chat_history=chat_history,
        current_date=current_date,
        language=language
    )

    # Stream output from LLM
    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content

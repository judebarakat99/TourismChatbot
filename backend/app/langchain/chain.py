from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from .prompts import prompt
import os

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    temperature=0.3,
    streaming=True,
    openai_api_version=os.getenv("OPENAI_API_CHAT_VERSION")
)

chain = prompt | llm


def stream_answer(
    question: str,
    context: str,
    chat_history: str,
    current_date: str,
    language: str = "en"
):
    inputs = {
        "question": question,
        "context": context,
        "chat_history": chat_history,
        "current_date": current_date,
        "language": language
    }

    for chunk in chain.stream(inputs):
        if chunk.content:
            yield chunk.content

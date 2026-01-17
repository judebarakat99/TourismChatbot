# app/langchain/rag.py
from datetime import date
from app.langchain.chain import stream_answer
from app.qdrant.retrieval import retrieve_context

def ask_tourism_bot(question: str, chat_history: str = "", language: str = "en"):
    """Retrieve context from Qdrant and stream an LLM response."""
    # Retrieve context from vector DB
    context = retrieve_context(question)

    # Stream answer from LangChain
    for token in stream_answer(
        question=question,
        context=context,
        chat_history=chat_history,
        current_date=str(date.today()),
        language=language
    ):
        yield token

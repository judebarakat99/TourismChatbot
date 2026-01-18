# app/langchain/rag.py
from datetime import date
from app.langchain.chain import stream_answer
from app.qdrant.retrieval import retrieve_context

def ask_tourism_bot(question: str, chat_history: str = "", language: str = "en"):
    """Retrieve context from Qdrant and stream an LLM response."""
    try:
        # Retrieve context from vector DB
        context = retrieve_context(question)
        print(f"Retrieved {len(context)} chars of context")

        # Stream answer from LangChain
        for token in stream_answer(
            question=question,
            context=context,
            chat_history=chat_history,
            current_date=str(date.today()),
            language=language
        ):
            yield token
    except Exception as e:
        print(f"Error in ask_tourism_bot: {str(e)}")
        yield ""

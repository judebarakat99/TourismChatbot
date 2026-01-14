from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from datetime import date
from app.langchain.rag import ask_tourism_bot

app = FastAPI(title="Tourism Chatbot API")

@app.get("/chat")
def chat(
    question: str,
    language: str = "en"
):
    def event_stream():
        for token in ask_tourism_bot(
            question=question,
            chat_history="",
            language=language
        ):
            yield f"data: {token}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )

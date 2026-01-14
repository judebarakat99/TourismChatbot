
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from typing import Dict, List
from uuid import uuid4
from app.langchain.rag import ask_tourism_bot

app = FastAPI(title="Tourism Chatbot API")

# In-memory sessions for current app lifetime
# Structure: { session_id: [ { "role": "user"|"assistant", "content": str }, ... ] }
sessions: Dict[str, List[Dict[str, str]]] = {}

SESSION_COOKIE_NAME = "session_id"


def _history_to_text(history: List[Dict[str, str]]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)



GLOBAL_SESSION_ID = "app_session"

@app.get("/chat")
def chat(question: str, language: str = "en"):
    history = sessions.get(GLOBAL_SESSION_ID, [])
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    def event_stream():
        answer_tokens = []
        for token in ask_tourism_bot(question, chat_history, language):
            answer_tokens.append(token)
            yield f"data: {token}\n\n"

        full_answer = "".join(answer_tokens)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": full_answer})
        sessions[GLOBAL_SESSION_ID] = history

    return StreamingResponse(event_stream(), media_type="text/event-stream")
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, List
from app.langchain.rag import ask_tourism_bot

# Initialize FastAPI application with a title
app = FastAPI(title="Tourism Chatbot API")

# In-memory session storage for the lifetime of the app
# Structure:
# {
#   session_id: [
#       { "role": "user"|"assistant", "content": str },
#       ...
#   ]
# }
sessions: Dict[str, List[Dict[str, str]]] = {}

# Using a single global session ID
GLOBAL_SESSION_ID = "app_session"


@app.get("/chat")
def chat(question: str, language: str = "en"):
    """
    GET endpoint for chatbot interaction.
    Accepts:
        - question: User's input text
        - language: Desired response language (default: 'en')
    Streams the assistant's response token-by-token using Server-Sent Events (SSE).
    """

    # Retrieve existing chat history for the global session
    history = sessions.get(GLOBAL_SESSION_ID, [])

    # Convert history into a text format for context
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    # Define a generator function to stream tokens as they are produced
    def event_stream():
        answer_tokens = []

        # Call the tourism bot and stream each token
        for token in ask_tourism_bot(question, chat_history, language):
            answer_tokens.append(token)
            # SSE format: "data: <token>\n\n"
            yield f"data: {token}\n\n"

        # Combine all tokens into the full answer
        full_answer = "".join(answer_tokens)

        # Update session history with user question and assistant response
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": full_answer})
        sessions[GLOBAL_SESSION_ID] = history

    # Return a streaming response so the client receives tokens progressively
    return StreamingResponse(event_stream(), media_type="text/event-stream")
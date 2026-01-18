from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import RAG, but have a fallback
try:
    from app.langchain.rag import ask_tourism_bot
    rag_available = True
except Exception as e:
    print(f"⚠️  RAG module not available: {e}")
    rag_available = False

# Initialize FastAPI application with a title
app = FastAPI(title="Tourism Chatbot API")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage for the lifetime of the app
# Structure:
# {
#   session_id: [
#       { "role": "user"|"assistant", "content": str },
#       ...
#   ]
# }
sessions: Dict[str, List[Dict[str, str]]] = {}

# Conversations storage
conversations: Dict[str, Dict] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"


@app.get("/health")
def health_check():
    """Health check endpoint for frontend to verify backend is running."""
    return {"status": "healthy", "service": "Tourism Chatbot API"}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    POST endpoint for streaming chat interaction.
    Accepts:
        - message: User's input text
        - session_id: Unique session identifier
        - language: Desired response language (default: 'en')
    Streams the assistant's response using Server-Sent Events (SSE).
    """
    
    session_id = request.session_id
    question = request.message
    language = request.language or "en"

    # Retrieve existing chat history for this session
    history = sessions.get(session_id, [])

    # Convert history into a text format for context
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    # Define a generator function to stream tokens as they are produced
    def event_stream():
        answer_tokens = []
        sources = []
        
        try:
            if rag_available:
                # Call the tourism bot and stream each token
                for token in ask_tourism_bot(question, chat_history, language):
                    answer_tokens.append(token)
                    # SSE format: "data: " followed by JSON and newline
                    response_data = {
                        "type": "content",
                        "content": token
                    }
                    yield f"data: {json.dumps(response_data)}\n"
            else:
                # Fallback response if RAG is not available
                fallback_response = f"I received your message: '{question}'. The AI system is currently initializing. Please ensure all dependencies are installed and Azure OpenAI credentials are configured."
                answer_tokens.append(fallback_response)
                response_data = {
                    "type": "content",
                    "content": fallback_response
                }
                yield f"data: {json.dumps(response_data)}\n"

            # Combine all tokens into the full answer
            full_answer = "".join(answer_tokens)

            # Update session history with user question and assistant response
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": full_answer})
            sessions[session_id] = history
            
            # Infer topic from the response (simplified)
            topic = "Italy Tourism"  # Default topic
            
            # Send completion event with metadata
            completion_data = {
                "type": "complete",
                "topic": topic,
                "sources": sources
            }
            yield f"data: {json.dumps(completion_data)}\n"
            
        except Exception as e:
            # Send error response
            error_data = {
                "type": "error",
                "content": f"Error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n"

    # Return a streaming response so the client receives tokens progressively
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    DELETE endpoint to remove a conversation.
    """
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
        return {"success": True, "message": f"Conversation {conversation_id} deleted"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/chat")
def chat(question: str, language: str = "en"):
    """
    GET endpoint for chatbot interaction (legacy endpoint).
    Accepts:
        - question: User's input text
        - language: Desired response language (default: 'en')
    Streams the assistant's response token-by-token using Server-Sent Events (SSE).
    """

    # Retrieve existing chat history for the global session
    GLOBAL_SESSION_ID = "app_session"
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
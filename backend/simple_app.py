from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI(title="Tourism Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions = {}
conversations = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Tourism Chatbot API"}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint with streaming"""
    
    session_id = request.session_id
    question = request.message
    language = request.language or "en"
    
    # Get history
    history = sessions.get(session_id, [])
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    async def event_stream():
        """Stream response in SSE format that matches frontend expectations"""
        # Sample tourism responses
        responses = {
            "rome": "Rome is the capital of Italy, known for its ancient history, incredible architecture, and world-famous landmarks like the Colosseum and the Vatican. It's one of the most visited cities in the world.",
            "venice": "Venice is a unique city built on water in northeastern Italy. Known for its canals, gondolas, and beautiful architecture, it's a UNESCO World Heritage Site and a must-visit destination.",
            "italy": "Italy is a beautiful Mediterranean country famous for its rich history, art, cuisine, and landscapes. From the rolling hills of Tuscany to the dramatic Amalfi Coast, Italy offers diverse experiences.",
            "tuscany": "Tuscany is a region in central Italy known for its stunning landscapes, rolling hills, vineyards, and charming medieval towns. It's perfect for wine tasting, cycling, and experiencing authentic Italian culture.",
            "default": "Thank you for your interest in Italy! It's a wonderful destination with rich history, amazing food, beautiful landscapes, and world-class art and architecture. What specific aspect would you like to know more about?"
        }
        
        # Select response based on question
        question_lower = question.lower()
        response_text = responses.get("default")
        
        for key, response in responses.items():
            if key in question_lower:
                response_text = response
                break
        
        # Stream response tokens one at a time in the CORRECT SSE format
        # Frontend expects: "event: token\ndata: <text>\n\n"
        for i, char in enumerate(response_text):
            # Send each character as a token event
            yield f"event: token\ndata: {char}\n\n"
            await asyncio.sleep(0.01)  # Small delay for streaming effect
        
        # Update history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response_text})
        sessions[session_id] = history
        
        # Send metadata event with sources
        sources_data = {
            "sources": [
                {"title": "Travel Guide", "source": "Italy Information"},
                {"title": "Tourism", "source": "Italian Tourism Board"}
            ]
        }
        yield f"event: meta\ndata: {json.dumps(sources_data)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
        return {"success": True, "message": f"Conversation deleted"}
    except Exception as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

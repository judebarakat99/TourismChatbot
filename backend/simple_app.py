from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Try to import LangChain components
try:
    from langchain_openai import AzureChatOpenAI
    from app.langchain.prompts import prompt
    from app.qdrant.retrieval import retrieve_context
    llm_available = True
except Exception as e:
    print(f"⚠️  LangChain/Azure OpenAI not available: {e}")
    llm_available = False
    llm = None

# Initialize Azure Chat LLM if available
if llm_available:
    try:
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
            temperature=0.3,
            streaming=True,
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        print("✅ Azure OpenAI LLM initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize Azure OpenAI: {e}")
        llm = None
        llm_available = False


class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if (llm_available and llm) else "degraded"
    return {"status": status, "service": "Tourism Chatbot API", "llm_available": llm_available}


def stream_answer_with_llm(
    question: str,
    context: str,
    chat_history: str,
    current_date: str,
    language: str = "en"
):
    """
    Stream answer using Azure OpenAI LLM.
    """
    try:
        # Format messages with the prompt
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
    except Exception as e:
        yield f"Error generating response: {str(e)}"


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint with streaming using RAG + LLM"""
    
    session_id = request.session_id
    question = request.message
    language = request.language or "en"
    
    # Get history
    history = sessions.get(session_id, [])
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    async def event_stream():
        """Stream response in SSE format"""
        try:
            if llm_available and llm:
                # Try to retrieve context from Qdrant
                try:
                    context = retrieve_context(question)
                except Exception as e:
                    print(f"⚠️  Could not retrieve context from Qdrant: {e}")
                    context = ""
                
                # Get response from LLM
                response_text = ""
                for token in stream_answer_with_llm(
                    question=question,
                    context=context,
                    chat_history=chat_history,
                    current_date=str(date.today()),
                    language=language
                ):
                    response_text += token
                    # Stream each character
                    for char in token:
                        yield f"event: token\ndata: {char}\n\n"
                        await asyncio.sleep(0.01)
            else:
                # Fallback: Use simple keyword-based responses
                response_text = get_fallback_response(question)
                for char in response_text:
                    yield f"event: token\ndata: {char}\n\n"
                    await asyncio.sleep(0.01)
            
            # Update history
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": response_text})
            sessions[session_id] = history
            
            # Send metadata with sources
            sources_data = {
                "sources": [
                    {"title": "Travel Guide", "source": "Italy Information"},
                    {"title": "Tourism", "source": "Italian Tourism Board"}
                ]
            }
            yield f"event: meta\ndata: {json.dumps(sources_data)}\n\n"
            
        except Exception as e:
            print(f"❌ Error in chat_stream: {e}")
            yield f"event: token\ndata: Error: {str(e)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


def get_fallback_response(question: str) -> str:
    """Fallback responses when LLM is not available"""
    responses = {
        "rome": "Rome is the capital of Italy, known for its ancient history, incredible architecture, and world-famous landmarks like the Colosseum and the Vatican. It's one of the most visited cities in the world.",
        "venice": "Venice is a unique city built on water in northeastern Italy. Known for its canals, gondolas, and beautiful architecture, it's a UNESCO World Heritage Site and a must-visit destination.",
        "italy": "Italy is a beautiful Mediterranean country famous for its rich history, art, cuisine, and landscapes. From the rolling hills of Tuscany to the dramatic Amalfi Coast, Italy offers diverse experiences.",
        "tuscany": "Tuscany is a region in central Italy known for its stunning landscapes, rolling hills, vineyards, and charming medieval towns. It's perfect for wine tasting, cycling, and experiencing authentic Italian culture.",
        "trip": "For a trip to Italy, I recommend visiting Rome for history, Venice for its unique charm, and Tuscany for wine and countryside. Plan at least 10-14 days to experience the best of what Italy has to offer.",
        "3 day": "For a 3-day trip, I recommend: Day 1 - Arrive in Rome and explore the Colosseum, Roman Forum, and Vatican. Day 2 - Day trip to Pompeii or relax in Rome. Day 3 - Visit Florence for Renaissance art and culture.",
        "default": "I'm here to help with your Italy travel questions! Ask me about destinations, itineraries, food, culture, or anything related to Italian tourism."
    }
    
    question_lower = question.lower()
    
    # Check for specific keywords
    for key, response in responses.items():
        if key in question_lower:
            return response
    
    return responses["default"]


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
        return {"success": True, "message": f"Conversation deleted"}
    except Exception as e:
        return {"success": False, "message": str(e)}




@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint with streaming using RAG + LLM"""
    
    session_id = request.session_id
    question = request.message
    language = request.language or "en"
    
    # Get history
    history = sessions.get(session_id, [])
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    async def event_stream():
        """Stream response in SSE format"""
        try:
            if llm_available and llm:
                # Try to retrieve context from Qdrant
                try:
                    context = retrieve_context(question)
                except Exception as e:
                    print(f"⚠️  Could not retrieve context from Qdrant: {e}")
                    context = ""
                
                # Get response from LLM
                response_text = ""
                for token in stream_answer_with_llm(
                    question=question,
                    context=context,
                    chat_history=chat_history,
                    current_date=str(date.today()),
                    language=language
                ):
                    response_text += token
                    # Stream each character
                    for char in token:
                        yield f"event: token\ndata: {char}\n\n"
                        await asyncio.sleep(0.01)
            else:
                # Fallback: Use simple keyword-based responses
                response_text = get_fallback_response(question)
                for char in response_text:
                    yield f"event: token\ndata: {char}\n\n"
                    await asyncio.sleep(0.01)
            
            # Update history
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": response_text})
            sessions[session_id] = history
            
            # Send metadata with sources
            sources_data = {
                "sources": [
                    {"title": "Travel Guide", "source": "Italy Information"},
                    {"title": "Tourism", "source": "Italian Tourism Board"}
                ]
            }
            yield f"event: meta\ndata: {json.dumps(sources_data)}\n\n"
            
        except Exception as e:
            print(f"❌ Error in chat_stream: {e}")
            yield f"event: token\ndata: Error: {str(e)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


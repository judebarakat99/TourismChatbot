# app/langchain/test_rag.py
from app.langchain.rag import ask_tourism_bot

question = "Tell me about popular events in Jordan this summer."
chat_history = ""  # Start empty for first question

print("✅ Streaming RAG response:")
for token in ask_tourism_bot(question, chat_history):
    print(token, end="", flush=True)
print("\n✅ Done!")

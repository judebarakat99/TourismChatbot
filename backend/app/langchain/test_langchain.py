from datetime import date
from app.langchain.chain import stream_answer, llm
from langchain_core.messages import HumanMessage

# ✅ Minimal connection test to Azure LLM
def test_connection():
    print("💡 Testing connection to Azure LLM...")
    try:
        for chunk in llm.stream([HumanMessage(content="Hello from LangChain test!")]):
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print("\n✅ Connection successful!\n")
    except Exception as e:
        print("❌ Connection failed:", e)

# ✅ Test prompt + streaming
def test_streaming_answer():
    question = "What are popular tourist attractions in France?"
    context = """
The Eiffel Tower is one of the most visited landmarks in Paris.
The Louvre Museum is the world's largest art museum.
"""
    print("💡 Testing stream_answer() with context...\n")
    for token in stream_answer(
        question=question,
        context=context,
        chat_history="",
        current_date=str(date.today()),
        language="en"
    ):
        print(token, end="", flush=True)
    print("\n✅ Streaming test complete!")

# Run tests
if __name__ == "__main__":
    test_connection()
    test_streaming_answer()

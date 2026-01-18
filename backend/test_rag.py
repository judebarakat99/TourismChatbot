#!/usr/bin/env python3
"""
Simple test to debug the RAG pipeline
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing RAG Pipeline")
print("=" * 60)

# Test 1: Import LangChain
print("\n1. Testing LangChain imports...")
try:
    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    print("   ✅ LangChain imports OK")
except Exception as e:
    print(f"   ❌ LangChain import failed: {e}")
    sys.exit(1)

# Test 2: Import Qdrant
print("\n2. Testing Qdrant...")
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(url="http://localhost:6333")
    collections = client.get_collections()
    print(f"   ✅ Qdrant connected. Collections: {[c.name for c in collections.collections]}")
except Exception as e:
    print(f"   ❌ Qdrant connection failed: {e}")

# Test 3: Test retrieve_context
print("\n3. Testing retrieve_context...")
try:
    from app.qdrant.retrieval import retrieve_context
    context = retrieve_context("Rome attractions")
    if context:
        print(f"   ✅ Retrieved {len(context)} chars of context")
        print(f"   Context preview: {context[:200]}...")
    else:
        print(f"   ⚠️  No context returned")
except Exception as e:
    print(f"   ❌ retrieve_context failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test prompt
print("\n4. Testing ChatPromptTemplate...")
try:
    from app.langchain.prompts import prompt
    print(f"   ✅ Prompt template loaded")
    print(f"   Input variables: {prompt.input_variables}")
except Exception as e:
    print(f"   ❌ Prompt loading failed: {e}")

# Test 5: Test LLM initialization
print("\n5. Testing Azure OpenAI LLM...")
try:
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),  
        temperature=0.3,
        streaming=True,
        openai_api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_CHAT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    print(f"   ✅ Azure OpenAI LLM initialized")
except Exception as e:
    print(f"   ❌ LLM initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test chain
print("\n6. Testing chain...")
try:
    from app.langchain.prompts import prompt
    chain = prompt | llm
    
    test_input = {
        "question": "Tell me about Rome",
        "context": "Rome is the capital of Italy.",
        "chat_history": "",
        "current_date": "2026-01-18",
        "language": "en"
    }
    
    print("   🔄 Streaming response from chain...")
    token_count = 0
    for chunk in chain.stream(test_input):
        if hasattr(chunk, 'content') and chunk.content:
            token_count += 1
            print(f"      Token {token_count}: {chunk.content[:50]}")
            if token_count >= 3:  # Just show first 3 tokens
                print("      ...")
                break
    
    if token_count > 0:
        print(f"   ✅ Chain streaming works (got {token_count}+ tokens)")
    else:
        print(f"   ⚠️  No tokens received from chain")
        
except Exception as e:
    print(f"   ❌ Chain test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

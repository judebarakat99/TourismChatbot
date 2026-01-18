import os
from dotenv import load_dotenv

load_dotenv()

# Check .env values
print("=== ENVIRONMENT VARIABLES ===")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_CHAT_API_VERSION")

print(f"API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")

# Test if endpoint has trailing slash
print(f"\nEndpoint ends with slash: {endpoint.endswith('/')}")

# Try to make a direct API call to test credentials
print("\n=== TESTING AZURE CREDENTIALS ===")
try:
    import requests
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Remove trailing slash for the test
    test_endpoint = endpoint.rstrip('/')
    
    # Try a simple test - get the deployment info
    test_url = f"{test_endpoint}/openai/deployments/{deployment}?api-version={api_version}"
    print(f"Test URL: {test_url}")
    
    response = requests.get(test_url, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
except Exception as e:
    print(f"Error testing credentials: {e}")

# Now test LangChain initialization
print("\n=== TESTING LANGCHAIN ===")
try:
    from langchain_openai import AzureChatOpenAI
    
    llm = AzureChatOpenAI(
        azure_deployment=deployment,  
        temperature=0.3,
        streaming=True,
        openai_api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    print("✅ LangChain AzureChatOpenAI initialized successfully")
    
    # Try a simple invocation
    result = llm.invoke("Hello, say 'test passed' if you can hear me")
    print(f"✅ LLM Response: {result}")
    
except Exception as e:
    print(f"❌ LangChain Error: {e}")
    import traceback
    traceback.print_exc()

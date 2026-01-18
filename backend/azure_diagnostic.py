#!/usr/bin/env python3
"""
Comprehensive Azure OpenAI diagnostics
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_env_variables():
    """Check all required environment variables"""
    print("=" * 60)
    print("1. ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    
    required_vars = {
        "AZURE_OPENAI_API_KEY": "Chat API Key",
        "AZURE_OPENAI_ENDPOINT_CHAT": "Chat Endpoint",
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "Chat Deployment",
        "AZURE_OPENAI_CHAT_API_VERSION": "Chat API Version",
        "AZURE_OPENAI_EMBEDDING_KEY": "Embedding API Key",
        "AZURE_OPENAI_ENDPOINT": "Embedding Endpoint",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "Embedding Deployment",
        "AZURE_OPENAI_EMBEDDING_API_VERSION": "Embedding API Version",
    }
    
    all_present = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            if "KEY" in var or "api_key" in var.lower():
                display = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value
            else:
                display = value
            print(f"✅ {desc:30} {var}: {display}")
        else:
            print(f"❌ {desc:30} {var}: NOT SET")
            all_present = False
    
    return all_present

def check_azure_cli_auth():
    """Check if Azure CLI is authenticated"""
    print("\n" + "=" * 60)
    print("2. AZURE CLI AUTHENTICATION CHECK")
    print("=" * 60)
    
    import subprocess
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            import json
            account = json.loads(result.stdout)
            print(f"✅ Azure CLI authenticated")
            print(f"   Subscription: {account.get('id')}")
            print(f"   Tenant: {account.get('tenantId')}")
            return True
        else:
            print(f"❌ Azure CLI not authenticated")
            print(f"   Run: az login")
            return False
    except Exception as e:
        print(f"⚠️  Azure CLI check failed: {e}")
        return False

def check_openai_library_version():
    """Check OpenAI library version"""
    print("\n" + "=" * 60)
    print("3. OPENAI LIBRARY VERSION CHECK")
    print("=" * 60)
    
    try:
        import openai
        print(f"✅ OpenAI library version: {openai.__version__}")
        return True
    except Exception as e:
        print(f"❌ Error checking OpenAI version: {e}")
        return False

def test_direct_api_call():
    """Test direct API call to Azure"""
    print("\n" + "=" * 60)
    print("4. DIRECT API CALL TEST")
    print("=" * 60)
    
    import requests
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
    deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_CHAT_API_VERSION")
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Check deployment exists
    test_url = f"{endpoint}/openai/deployments/{deployment}?api-version={api_version}"
    print(f"\nTest URL: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print(f"❌ Deployment '{deployment}' not found at this resource")
            print(f"   This could mean:")
            print(f"   - Deployment name is incorrect")
            print(f"   - Deployment doesn't exist in this resource")
            print(f"   - API key is for a different resource")
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401)")
            print(f"   - API key might be invalid or expired")
            print(f"   - API key might not have permissions")
        else:
            print(f"Response: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_langchain_initialization():
    """Test LangChain initialization"""
    print("\n" + "=" * 60)
    print("5. LANGCHAIN INITIALIZATION TEST")
    print("=" * 60)
    
    try:
        from langchain_openai import AzureChatOpenAI
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_CHAT")
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_CHAT_API_VERSION")
        
        print(f"Initializing with:")
        print(f"  Endpoint: {endpoint}")
        print(f"  Deployment: {deployment}")
        print(f"  API Version: {api_version}")
        
        llm = AzureChatOpenAI(
            azure_deployment=deployment,
            temperature=0.3,
            streaming=False,  # Don't stream for this test
            openai_api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key,
        )
        print(f"✅ LangChain AzureChatOpenAI initialized successfully")
        
        # Try simple call
        print(f"\nAttempting to invoke LLM with test prompt...")
        result = llm.invoke("Say 'API connection works' if you can hear me.")
        print(f"✅ LLM Response: {result.content[:100]}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  AZURE OPENAI DIAGNOSTIC TOOL".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {
        "Env Variables": check_env_variables(),
        "OpenAI Library": check_openai_library_version(),
        "Direct API Call": test_direct_api_call(),
        "LangChain Init": test_langchain_initialization(),
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Azure OpenAI is properly configured")
    else:
        print("❌ SOME TESTS FAILED - See above for details")
        print("\nCommon fixes:")
        print("1. Check API key is correct and not expired")
        print("2. Verify deployment name exists in Azure Portal")
        print("3. Ensure API key subscription matches the resource")
        print("4. Check endpoint URL is correct (no trailing slash)")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

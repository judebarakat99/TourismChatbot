from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.5,
    streaming=False,
    openai_api_version=os.getenv("OPENAI_API_VERSION")
)

# Prepare messages (single conversation in a batch)
messages = [[HumanMessage(content="Tell me about popular tourist attractions in Paris.")]]  

# Generate response
response = llm.generate(messages)

# ✅ Correct way to print text for your version
print("✅ Answer:")
print(response.generations[0][0].text)

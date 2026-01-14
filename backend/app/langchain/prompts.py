from langchain_core.prompts import ChatPromptTemplate

# Define a reusable chat prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a professional tourism assistant.

Current date: {current_date}

Use ONLY the provided context to answer.
If the answer is not in the context, say you don't know.

Respond in {language}.
"""
    ),
    (
        "human",
        """
Conversation history:
{chat_history}

Context:
{context}

User question:
{question}
"""
    )
])

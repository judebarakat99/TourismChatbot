from langchain_core.prompts import ChatPromptTemplate

# Define a reusable chat prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a professional tourism assistant.

Current date: {current_date}

Use only the provided context to answer.
If the answer is not in the context, say you don't know.
When using information, mention all the source document names in your answer as Source:[source] at the end of your answer.
If no documents are used in the current answer, do not mention any sources.    

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

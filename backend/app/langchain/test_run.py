from datetime import date
from app.langchain.chain import stream_answer

question = "What are popular tourist attractions in France?"

context = """
The Eiffel Tower is one of the most visited landmarks in Paris.
The Louvre Museum is the world's largest art museum.
"""

for token in stream_answer(
    question=question,
    context=context,
    chat_history="",
    current_date=str(date.today()),
    language="en"
):
    print(token, end="", flush=True)

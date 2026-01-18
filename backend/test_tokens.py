from app.langchain.chain import stream_answer

context = "Rome is a beautiful city with incredible monuments and history."
question = "Tell me about Rome"

print("Token analysis:")
print("=" * 50)

tokens = []
for i, token in enumerate(stream_answer(question, context, '', '2026-01-18', 'en')):
    tokens.append(token)
    if i < 20:  # Print first 20 tokens
        print(f"Token {i+1:3d}: {repr(token):40s} len={len(token)}")

print("\n" + "=" * 50)
print(f"Total tokens: {len(tokens)}")
print(f"\nFull response:\n{''.join(tokens)}")

from app.langchain.chain import stream_answer
import traceback

try:
    print('Testing stream_answer...')
    context = 'Rome has incredible history and ancient monuments like the Colosseum and Vatican.'
    tokens = []
    for token in stream_answer('Tell me about Rome', context, '', '2026-01-18', 'en'):
        tokens.append(token)
        if len(tokens) <= 5:
            print(f'Token {len(tokens)}: {repr(token)}')
    print(f'Total tokens: {len(tokens)}')
    if tokens:
        response = "".join(tokens)
        print(f'Response preview: {repr(response[:100])}')
        print(f'Full response: {response}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()

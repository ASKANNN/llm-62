from ollama import chat

MODEL_NAME = 'phi3'


def chat_request(messages):
    stream = chat(model=MODEL_NAME, messages=messages, stream=True)
    full_reply = ''
    for chunk in stream:
        piece = chunk['message']['content']
        print(piece, end='', flush=True)
        full_reply += piece
    return full_reply


def main():
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful assistant. Answer briefly and clearly.'
        }
    ]
    print('phi-3 simple chat. Type "exit" to quit.')
    while True:
        user_input = input('You: ')
        if user_input == 'exit':
            print('Bye')
            break
        messages.append({
            'role': 'user',
            'content': user_input
        })
        print('\nAgent:', end='', flush=True)
        reply = chat_request(messages)
        messages.append({
            'role': 'assistant',
            'content': reply
        })
        print()
        print('_' * 60)


main()

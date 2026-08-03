# pip install ollama

import ollama

MODEL_NAME = 'phi3'


def chat_request(messages):
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return response['message']['content']


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
        reply = chat_request(messages)
        messages.append({
            'role': 'assistant',
            'content': reply
        })
        print('\nAgent:', reply)
        print('_' * 60)


main()

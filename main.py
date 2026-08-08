import asyncio
import json
from ollama import AsyncClient
from tools import TOOLS
from system_content import SYSTEM_CONTENT

MODEL_NAME = 'phi3'

client = AsyncClient()


async def chat_request(messages):
    full_reply = ''
    try:
        stream = await client.chat(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            options={'num_predict': 300}
        )
        async for chunk in stream:
            piece = chunk['message']['content']
            print(piece, end='', flush=True)
            full_reply += piece
    except Exception as e:
        print(f"Error: {e}", end='')
    print()
    return full_reply


def parse_tool_call(text):
    start = text.find('{')
    if start == -1:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) and 'tool' in data else None


async def call_tool(tool_call: dict):
    tool = TOOLS.get(tool_call.get('tool'))
    if not tool:
        return None
    try:
        return await tool(**tool_call.get('arguments', {}))
    except TypeError:
        return "Could not call the tool: missing or invalid arguments"


async def main():
    messages = [
        {
            'role': 'system',
            'content': SYSTEM_CONTENT
        }
    ]
    print('phi-3 simple chat. Type "exit" to quit.')
    while True:
        user_input = input('You: ')
        if user_input == 'exit':
            print('Bye')
            break
        if not user_input.strip():
            continue
        messages.append({
            'role': 'user',
            'content': user_input
        })
        print('\nAgent:', end='', flush=True)
        reply = await chat_request(messages)
        messages.append({
            'role': 'assistant',
            'content': reply
        })
        tool_call = parse_tool_call(reply)
        if tool_call:
            messages[-1]['content'] = json.dumps(tool_call)
            tool_result = await call_tool(tool_call)
            if tool_result:
                messages.append({
                    'role': 'system',
                    'content': f"Tool result: {tool_result}\nAnswer the user's last question using exactly these values and units. Do not convert units or invent any numbers."
                })
                print('\nAgent:', end='', flush=True)
                reply = await chat_request(messages)
                messages.append({
                    'role': 'assistant',
                    'content': reply
                })
        print('_' * 60)


if __name__ == '__main__':
    asyncio.run(main())

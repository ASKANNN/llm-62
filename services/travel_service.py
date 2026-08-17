import json
import os

import httpx
from ollama import AsyncClient

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
FIXER_API_KEY = os.environ.get('FIXER_API_KEY')

GEOCODE_URL = 'https://api.openweathermap.org/geo/1.0/direct'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
FIXER_URL = 'https://api.apilayer.com/fixer/latest'
OLLAMA_MODEL = 'qwen2.5:3b'

ollama_client = AsyncClient()


def _extract_json(text: str) -> dict:
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"Ollama response does not contain JSON: {text!r}")
    return json.loads(text[start:end + 1])


async def get_country_info(country: str) -> dict | None:
    prompt = (
        'Return ONLY valid JSON with EXACTLY these keys: '
        '{"capital": "...", "currency_code": "...", "currency_name": "..."}\n'
        f'capital = capital city of {country}\n'
        f'currency_code = 3-letter ISO currency code of {country}\n'
        f'currency_name = English name of that currency\n'
        'Do not add extra keys. Do not use Markdown.'
    )
    response = await ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
    )

    try:
        data = _extract_json(response['message']['content'])
    except ValueError:
        return None

    capital = data.get('capital')
    currency_code = data.get('currency_code')
    currency_name = data.get('currency_name')
    if not capital or not currency_code or not currency_name:
        return None

    return {
        'capital': capital,
        'currency_code': currency_code,
        'currency_name': currency_name,
    }


async def get_exchange_rate(code_from: str, code_to: str) -> float | None:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            FIXER_URL,
            params={'base': code_from, 'symbols': code_to},
            headers={'apikey': FIXER_API_KEY},
        )

    if resp.status_code != 200:
        return None

    data = resp.json()
    if not data.get('success', True):
        return None

    return data.get('rates', {}).get(code_to)


async def get_weather(city: str) -> str | None:
    async with httpx.AsyncClient() as client:
        geo_resp = await client.get(GEOCODE_URL, params={'q': city, 'limit': 1, 'appid': WEATHER_API_KEY})
        geo_data = geo_resp.json()
        if geo_resp.status_code != 200 or not geo_data:
            return None

        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
        resp = await client.get(WEATHER_URL, params={'lat': lat, 'lon': lon, 'units': 'metric', 'appid': WEATHER_API_KEY})

    if resp.status_code != 200:
        return None

    data = resp.json()
    temperature = data.get('main', {}).get('temp')
    humidity = data.get('main', {}).get('humidity')
    condition = data.get('weather', [{}])[0].get('description')
    wind_speed = data.get('wind', {}).get('speed')

    if any(field is None for field in (temperature, humidity, condition, wind_speed)):
        return None

    return f'Temperature: {temperature}°C, Humidity: {humidity}%, Condition: {condition}, Wind speed: {wind_speed} m/s'

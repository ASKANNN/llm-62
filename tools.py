import requests
import os

URL = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = os.environ.get('WEATHER_API_KEY')

if not API_KEY:
    raise RuntimeError("API_KEY is not set")


def get_weather(city):
    try:
        resp = requests.get(URL, params={'q': city, 'units': 'metric', 'appid': API_KEY})
    except requests.RequestException:
        return f"Could not reach the weather service for {city}"

    data = resp.json()
    if resp.status_code != 200:
        return f"Could not get weather for {city}"

    temp = data.get('main', {}).get('temp')
    if temp is None:
        return f"Could not get temperature for {city}"

    return f'Temperature in {city} = {temp}°C'


TOOLS = {
    'get_weather': get_weather
}

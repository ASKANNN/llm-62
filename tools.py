import httpx
import os

GEOCODE_URL = 'https://api.openweathermap.org/geo/1.0/direct'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = os.environ.get('WEATHER_API_KEY')

if not API_KEY:
    raise RuntimeError("API_KEY is not set")


async def get_weather(city, country=None):
    geo_query = f'{city},{country}' if country else city
    try:
        async with httpx.AsyncClient() as client:
            geo_resp = await client.get(GEOCODE_URL, params={'q': geo_query, 'limit': 1, 'appid': API_KEY})
            geo_data = geo_resp.json()
            if geo_resp.status_code != 200 or not geo_data:
                return f"Could not get weather for {city}"

            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            resp = await client.get(WEATHER_URL, params={'lat': lat, 'lon': lon, 'units': 'metric', 'appid': API_KEY})
    except httpx.RequestError:
        return f"Could not reach the weather service for {city}"

    data = resp.json()
    if resp.status_code != 200:
        return f"Could not get weather for {city}"

    temperature = data.get('main', {}).get('temp')
    country_code = data.get('sys', {}).get('country')
    wind_spd = data.get('wind', {}).get('speed')
    vis = data.get('visibility')
    cloudiness = data.get('clouds', {}).get('all')
    weather_fields = [temperature, country_code, wind_spd, vis, cloudiness]
    if any(field is None for field in weather_fields):
        return f"Could not get all details of weather for {city}"

    return (f'Weather in {country_code}: {city}. Temperature = {temperature}°C, '
            f'Wind speed = {wind_spd}, Visibility = {vis}, Clouds = {cloudiness}')


TOOLS = {
    'get_weather': get_weather
}

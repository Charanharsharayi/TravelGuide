import requests
from app.core.config import settings
from app.agents.state import AgentState
from datetime import datetime, timedelta


def _geocode_city(city_name: str) -> dict:
    """Convert city name to lat/lon using OpenWeatherMap Geocoding API."""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "limit": 1,
        "appid": settings.OPENWEATHERMAP_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0].get("name", city_name)}
    except Exception as e:
        print(f"Geocoding error for '{city_name}': {e}")
    return {}


def _get_weather_forecast(lat: float, lon: float, trip_date_str: str) -> dict:
    """
    Fetch weather data from OpenWeatherMap.
    Uses 5-day forecast for near dates, current weather for farther dates.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    if not api_key:
        return {"error": "OpenWeatherMap API key not configured"}

    try:
        trip_date = datetime.strptime(trip_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        trip_date = None

    today = datetime.now().date()
    days_ahead = (trip_date - today).days if trip_date else 999

    result = {}

    if days_ahead <= 5 and days_ahead >= 0:
        # Use 5-day / 3-hour forecast API (free tier)
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Find forecasts closest to the trip date
            target_str = trip_date_str
            temps = []
            descriptions = set()
            for item in data.get("list", []):
                if item["dt_txt"].startswith(target_str):
                    temps.append(item["main"]["temp"])
                    descriptions.add(item["weather"][0]["description"])

            if temps:
                result = {
                    "temp_min": round(min(temps), 1),
                    "temp_max": round(max(temps), 1),
                    "conditions": ", ".join(descriptions),
                    "source": "5-day forecast",
                }
        except Exception as e:
            print(f"Forecast API error: {e}")

    if not result:
        # Fallback: use current weather + seasonal estimation
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            current_temp = data["main"]["temp"]
            description = data["weather"][0]["description"]

            # If trip is in a different month, add a rough seasonal note
            if trip_date:
                month = trip_date.strftime("%B")
                result = {
                    "temp_min": round(current_temp - 3, 1),
                    "temp_max": round(current_temp + 3, 1),
                    "conditions": description,
                    "source": f"estimated for {month} (based on current weather)",
                }
            else:
                result = {
                    "temp_min": round(current_temp - 2, 1),
                    "temp_max": round(current_temp + 2, 1),
                    "conditions": description,
                    "source": "current weather",
                }
        except Exception as e:
            print(f"Current weather API error: {e}")
            result = {"error": str(e)}

    return result


def weather_node(state: AgentState):
    """
    Fetches weather data for the destination using OpenWeatherMap API.
    Returns weather context string for the planner.
    """
    request = state.get("trip_request")
    if not request:
        return {"weather_context": "No trip request found."}

    destination = request.destination or request.query
    trip_date = request.trip_date or ""

    # Geocode the destination
    geo = _geocode_city(destination)
    if not geo:
        return {"weather_context": f"Could not find weather data for '{destination}'. Plan for moderate weather."}

    # Fetch weather
    weather = _get_weather_forecast(geo["lat"], geo["lon"], trip_date)

    if "error" in weather:
        return {"weather_context": f"Weather lookup failed: {weather['error']}. Plan for moderate weather."}

    context = (
        f"Weather for {geo['name']} around {trip_date or 'upcoming dates'}:\n"
        f"  Temperature: {weather['temp_min']}°C to {weather['temp_max']}°C\n"
        f"  Conditions: {weather['conditions']}\n"
        f"  Source: {weather['source']}\n"
        f"\nUse this to recommend appropriate clothing, gear, and activities."
    )

    print(f"Weather context: {context}")
    return {"weather_context": context}

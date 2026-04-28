import requests
import pandas as pd
from datetime import datetime
import os


# Tucson / Vail area coordinates
latitude = 32.0478
longitude = -110.7120

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,

    # Current weather fields
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code",

    # Hourly weather fields
    "hourly": "temperature_2m,precipitation_probability",

    # Daily weather fields
    "daily": "temperature_2m_max,temperature_2m_min,weather_code",

    # Fahrenheit and local time
    "temperature_unit": "fahrenheit",
    "timezone": "auto"
}


response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

# Make sure folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)


# -------------------------
# Current weather
# -------------------------
current = pd.DataFrame([data["current"]])
current.to_csv("data/current_weather.csv", index=False)


# -------------------------
# Daily forecast
# -------------------------
daily = pd.DataFrame(data["daily"])
daily.to_csv("data/daily_weather.csv", index=False)


# -------------------------
# Hourly forecast
# -------------------------
hourly = pd.DataFrame(data["hourly"])
hourly.to_csv("data/hourly_weather.csv", index=False)


# -------------------------
# Text report
# -------------------------
current_temp = data["current"]["temperature_2m"]
humidity = data["current"]["relative_humidity_2m"]
feels_like = data["current"]["apparent_temperature"]
weather_code = data["current"]["weather_code"]
report_time = data["current"]["time"]

today_high = data["daily"]["temperature_2m_max"][0]
today_low = data["daily"]["temperature_2m_min"][0]

report = f"""
Weather Report
Generated: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}

Location:
Latitude: {latitude}
Longitude: {longitude}

Current Weather:
Time: {report_time}
Temperature: {current_temp}°F
Feels Like: {feels_like}°F
Humidity: {humidity}%
Weather Code: {weather_code}

Today's Forecast:
High: {today_high}°F
Low: {today_low}°F
"""

with open("output/weather_report.txt", "w") as file:
    file.write(report)


print("Weather data saved successfully.")
print("Files created:")
print("data/current_weather.csv")
print("data/daily_weather.csv")
print("data/hourly_weather.csv")
print("output/weather_report.txt")

import pandas as pd
from datetime import datetime
import os


# Tucson / Vail area coordinates
latitude = 32.0478
longitude = -110.7120

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,

    # Current weather fields
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code",

    # Hourly weather fields
   "hourly": "temperature_2m,precipitation_probability,weather_code",

    # Daily weather fields
    "daily": "temperature_2m_max,temperature_2m_min,weather_code",

    # Fahrenheit and local time
    "temperature_unit": "fahrenheit",
    "timezone": "auto"
}


response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

# Make sure folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)


# -------------------------
# Current weather
# -------------------------
current = pd.DataFrame([data["current"]])
current.to_csv("data/current_weather.csv", index=False)


# -------------------------
# Daily forecast
# -------------------------
daily = pd.DataFrame(data["daily"])
daily.to_csv("data/daily_weather.csv", index=False)


# -------------------------
# Hourly forecast
# -------------------------
hourly = pd.DataFrame(data["hourly"])
hourly.to_csv("data/hourly_weather.csv", index=False)


# -------------------------
# Text report
# -------------------------
current_temp = data["current"]["temperature_2m"]
humidity = data["current"]["relative_humidity_2m"]
feels_like = data["current"]["apparent_temperature"]
weather_code = data["current"]["weather_code"]
report_time = data["current"]["time"]

today_high = data["daily"]["temperature_2m_max"][0]
today_low = data["daily"]["temperature_2m_min"][0]

report = f"""
Weather Report
Generated: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}

Location:
Latitude: {latitude}
Longitude: {longitude}

Current Weather:
Time: {report_time}
Temperature: {current_temp}°F
Feels Like: {feels_like}°F
Humidity: {humidity}%
Weather Code: {weather_code}

Today's Forecast:
High: {today_high}°F
Low: {today_low}°F
"""

with open("output/weather_report.txt", "w") as file:
    file.write(report)


print("Weather data saved successfully.")
print("Files created:")
print("data/current_weather.csv")
print("data/daily_weather.csv")
print("data/hourly_weather.csv")
print("output/weather_report.txt")
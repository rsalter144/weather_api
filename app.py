from flask import Flask, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def index():
    # Read weather data
    current = pd.read_csv("data/current_weather.csv")
    daily = pd.read_csv("data/daily_weather.csv")
    hourly = pd.read_csv("data/hourly_weather.csv")

    # Current weather
    current_row = current.iloc[0]

    current_temp = current_row["temperature_2m"]
    humidity = current_row["relative_humidity_2m"]
    feels_like = current_row["apparent_temperature"]
    weather_code = int(current_row.get("weather_code", 0) or 0)

    today = datetime.now().strftime("%Y-%m-%d")

    # 3-day forecast
    forecast_data = daily.head(3)
    forecast = []

    for _, row in forecast_data.iterrows():
        code = int(row.get("weather_code", 0) or 0)

        if code == 0:
            day_icon = "☀️"
            description = "Clear"
        elif code in [1, 2, 3]:
            day_icon = "⛅"
            description = "Partly Cloudy"
        elif code in [45, 48]:
            day_icon = "🌫️"
            description = "Fog"
        elif code in [51, 53, 55, 61, 63, 65]:
            day_icon = "🌧️"
            description = "Rain"
        elif code in [71, 73, 75]:
            day_icon = "❄️"
            description = "Snow"
        elif code in [95, 96, 99]:
            day_icon = "⛈️"
            description = "Thunderstorm"
        else:
            day_icon = "❓"
            description = "Unknown"

        forecast.append({
            "date": row["time"],
            "high": row["temperature_2m_max"],
            "low": row["temperature_2m_min"],
            "icon": day_icon,
            "description": description
        })

    # Hourly forecast
    hourly_forecast = []

    for _, row in hourly.head(6).iterrows():
        time_obj = datetime.fromisoformat(str(row["time"]))
        formatted_time = time_obj.strftime("%I %p").lstrip("0")

        code = int(row.get("weather_code", 0) or 0)

        if code == 0:
            icon = "☀️"
        elif code in [1, 2, 3]:
            icon = "⛅"
        elif code in [45, 48]:
            icon = "🌫️"
        elif code in [51, 53, 55, 61, 63, 65]:
            icon = "🌧️"
        elif code in [71, 73, 75]:
            icon = "❄️"
        elif code in [95, 96, 99]:
            icon = "⛈️"
        else:
            icon = "❓"

        hourly_forecast.append({
            "time": formatted_time,
            "temp": row["temperature_2m"],
            "precip": row["precipitation_probability"],
            "icon": icon
        })

    last_updated = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    return render_template(
        "index.html",
        today=today,
        current_temp=current_temp,
        humidity=humidity,
        feels_like=feels_like,
        weather_code=weather_code,
        forecast=forecast,
        hourly_forecast=hourly_forecast,
        last_updated=last_updated
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
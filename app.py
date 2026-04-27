from flask import Flask, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    try:
        daily = pd.read_csv("data/daily_weather.csv")
        current = pd.read_csv("data/current_weather.csv")

        daily["time"] = pd.to_datetime(daily["time"])

        latest_daily = daily.iloc[0]
        latest_current = current.iloc[-1]

        temp = float(latest_current["temperature_2m"])

        if temp > 85:
            icon = "☀️"
            temp_class = "hot"
        elif temp > 65:
            icon = "⛅"
            temp_class = "warm"
        else:
            icon = "🌧️"
            temp_class = "cool"

        forecast_data = daily.head(3)

        forecast = []

        for _, row in forecast_data.iterrows():
            code = row.get("weather_code", 0)

            try:
                code = int(code)
            except:
                code = 0

            if code == 0:
                day_icon = "☀️"
            elif code in [1, 2, 3]:
                day_icon = "⛅"
            else:
                day_icon = "🌧️"

            forecast.append({
                "date": row["time"].strftime("%a"),
                "high": row["temperature_2m_max"],
                "low": row["temperature_2m_min"],
                "icon": day_icon
            })
        
        weather = {
           
            "date": datetime.today().strftime("%Y-%m-%d"),
            "temp_max": latest_daily["temperature_2m_max"],
            "temp_min": latest_daily["temperature_2m_min"],
            "current_temp": latest_current["temperature_2m"],
            "humidity": latest_current["relative_humidity_2m"],
            "feels_like": latest_current["apparent_temperature"],
            "icon": icon,
            "temp_class": temp_class
        }

    except Exception as e:
        print("FULL ERROR:", e)
        weather = {}
        forecast = []

    return render_template("index.html", weather=weather, forecast=forecast)

if __name__ == "__main__":
    app.run(debug=True)
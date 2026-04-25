import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 32.0478,
        "longitude": -110.7120,
        "current": "temperature_2m,relative_humidity_2m",
        "temperature_unit": "fahrenheit"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        temperature = data["current"]["temperature_2m"]
        humidity = data["current"]["relative_humidity_2m"]

    except Exception as e:
        print("Error:", e)
        temperature = "N/A"
        humidity = "N/A"

    return render_template(
        "index.html",
        temperature=temperature,
        humidity=humidity
    )

if __name__ == "__main__":
    app.run(debug=True)
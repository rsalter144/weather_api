import requests
import pandas as pd
import argparse
from datetime import datetime
from pathlib import Path


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Download weather data from Open-Meteo and save it to CSV and text files."
    )

    parser.add_argument(
        "--city",
        type=str,
        help='City name, for example: "Tucson"'
    )

    parser.add_argument(
        "--lat",
        type=float,
        default=32.0478,
        help="Latitude (default: 32.0478)"
    )

    parser.add_argument(
        "--lon",
        type=float,
        default=-110.7120,
        help="Longitude (default: -110.7120)"
    )

    parser.add_argument(
        "--unit",
        choices=["fahrenheit", "celsius"],
        default="fahrenheit",
        help="Temperature unit (default: fahrenheit)"
    )

    parser.add_argument(
        "--timezone",
        default="auto",
        help='Timezone (default: "auto")'
    )

    parser.add_argument(
        "--output",
        default="weather_output",
        help='Output folder name (default: "weather_output")'
    )

    parser.add_argument(
        "--prefix",
        default="weather",
        help='Filename prefix (default: "weather")'
    )

    parser.add_argument(
        "--report" ,
        action="store_true" ,
        help="Generate text report"
    )

    return parser.parse_args()


def get_coordinates_from_city(city: str):
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(GEOCODE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        raise ValueError(f'City not found: {city}')

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    location_name = place["name"]
    admin1 = place.get("admin1", "")
    country = place.get("country", "")

    pretty_location = ", ".join(part for part in [location_name, admin1, country] if part)

    return latitude, longitude, pretty_location


def get_weather_data(latitude: float, longitude: float, unit: str, timezone: str):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature",
        "hourly": "temperature_2m,precipitation_probability",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": unit,
        "timezone": timezone
    }

    response = requests.get(FORECAST_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json(), response.url


def weather_code_to_text(code: int) -> str:
    code_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return code_map.get(code, f"Unknown ({code})")


def save_weather_data(data: dict, output_folder: Path, prefix: str):
    output_folder.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    current_df = pd.DataFrame([data["current"]])
    daily_df = pd.DataFrame(data["daily"])
    hourly_df = pd.DataFrame(data["hourly"])

    current_file = output_folder / f"{prefix}_current_{timestamp}.csv"
    daily_file = output_folder / f"{prefix}_daily_{timestamp}.csv"
    hourly_file = output_folder / f"{prefix}_hourly_{timestamp}.csv"

    current_df.to_csv(current_file, index=False)
    daily_df.to_csv(daily_file, index=False)
    hourly_df.to_csv(hourly_file, index=False)

    return current_file, daily_file, hourly_file, timestamp


def save_text_report(data: dict, output_folder: Path, prefix: str, timestamp: str, location_label: str, unit: str):
    degree_symbol = "°F" if unit == "fahrenheit" else "°C"

    current = data["current"]
    daily = data["daily"]

    today_code = daily["weather_code"][0]
    today_summary = weather_code_to_text(today_code)

    report_lines = [
        f"Weather Report for {location_label}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}",
        "",
        "Current Conditions",
        "------------------",
        f"Time: {current['time']}",
        f"Temperature: {current['temperature_2m']}{degree_symbol}",
        f"Feels Like: {current['apparent_temperature']}{degree_symbol}",
        f"Humidity: {current['relative_humidity_2m']}%",
        "",
        "Today's Forecast",
        "----------------",
        f"Conditions: {today_summary}",
        f"High: {daily['temperature_2m_max'][0]}{degree_symbol}",
        f"Low: {daily['temperature_2m_min'][0]}{degree_symbol}",
        f"Precipitation: {daily['precipitation_sum'][0]}",
        "",
        "Next Few Days",
        "-------------"
    ]

    for i in range(min(5, len(daily["time"]))):
        day = daily["time"][i]
        summary = weather_code_to_text(daily["weather_code"][i])
        high = daily["temperature_2m_max"][i]
        low = daily["temperature_2m_min"][i]
        precip = daily["precipitation_sum"][i]

        report_lines.append(
            f"{day}: {summary}, High {high}{degree_symbol}, Low {low}{degree_symbol}, Precip {precip}"
        )

    report_text = "\n".join(report_lines)

    report_file = output_folder / f"{prefix}_report_{timestamp}.txt"
    report_file.write_text(report_text, encoding="utf-8")

    return report_file, report_text


def display_summary(data: dict, unit: str, location_label: str):
    current = data["current"]
    daily = data["daily"]

    degree_symbol = "°F" if unit == "fahrenheit" else "°C"
    today_summary = weather_code_to_text(daily["weather_code"][0])

    print("\n" + "=" * 50)
    print(f"Weather for {location_label}")
    print("=" * 50)

    print("\nCurrent weather:")
    print(f"Time: {current['time']}")
    print(f"Temperature: {current['temperature_2m']}{degree_symbol}")
    print(f"Feels like: {current['apparent_temperature']}{degree_symbol}")
    print(f"Humidity: {current['relative_humidity_2m']}%")

    print("\nToday's forecast:")
    print(f"Conditions: {today_summary}")
    print(f"High: {daily['temperature_2m_max'][0]}{degree_symbol}")
    print(f"Low: {daily['temperature_2m_min'][0]}{degree_symbol}")
    print(f"Precipitation: {daily['precipitation_sum'][0]}")


def main():
    args = parse_arguments()

    try:
        if args.city:
            latitude, longitude, location_label = get_coordinates_from_city(args.city)
        else:
            latitude = args.lat
            longitude = args.lon
            location_label = f"Lat {latitude}, Lon {longitude}"

        data, request_url = get_weather_data(
            latitude=latitude,
            longitude=longitude,
            unit=args.unit,
            timezone=args.timezone
        )

        print("Request URL:")
        print(request_url)

        display_summary(data, args.unit, location_label)

        output_folder = Path(args.output)
        current_file, daily_file, hourly_file, timestamp = save_weather_data(
            data, output_folder, args.prefix
        )

        if args.report:
            report_file, _ = save_text_report(
                data=data,
                output_folder=output_folder,
                prefix=args.prefix,
                timestamp=timestamp,
                location_label=location_label,
                unit=args.unit
        )
        
        print(report_file)

        print("\nFiles saved:")
        print(current_file)
        print(daily_file)
        print(hourly_file)
        print(report_file)

    except requests.exceptions.Timeout:
        print("Error: The request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError as e:
        print(f"Missing expected data in API response: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
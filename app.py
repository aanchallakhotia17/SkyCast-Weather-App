import os
import requests
import mysql.connector

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "weather_forecasting")
    )


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    if filename in ("style.css", "script.js"):
        return send_from_directory(".", filename)
    return jsonify({"error": "File not found"}), 404


@app.route("/api/weather")
def get_weather():
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    if not API_KEY:
        return jsonify({"error": "Weather API key is missing."}), 500

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )

        if response.status_code == 404:
            return jsonify({"error": "City not found."}), 404

        if response.status_code == 401:
            return jsonify({
                "error": "Weather API key is invalid or not activated."
            }), 502

        response.raise_for_status()
        data = response.json()

        weather = {
            "city": f"{data['name']}, {data['sys']['country']}",
            "temperature": round(data["main"]["temp"]),
            "feelsLike": round(data["main"]["feels_like"]),
            "condition": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "humidity": data["main"]["humidity"],
            "windSpeed": round(data.get("wind", {}).get("speed", 0) * 3.6),
            "pressure": data["main"]["pressure"]
        }

        # Save the weather search in MySQL
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO weather_history
            (city, temperature, feels_like, humidity,
             wind_speed, pressure, weather_condition)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            weather["city"],
            data["main"]["temp"],
            data["main"]["feels_like"],
            weather["humidity"],
            data.get("wind", {}).get("speed", 0) * 3.6,
            weather["pressure"],
            weather["condition"]
        )

        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify(weather)

    except requests.Timeout:
        return jsonify({"error": "Weather service timed out."}), 504

    except requests.RequestException:
        return jsonify({"error": "Could not connect to weather service."}), 502

    except mysql.connector.Error:
        app.logger.exception("MySQL database error")
        return jsonify({
            "error": "Weather was fetched, but saving to MySQL failed. Check database settings."
        }), 500

    except (KeyError, IndexError, TypeError, ValueError):
        return jsonify({"error": "Unexpected weather data received."}), 502


@app.route("/api/history")
def get_history():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM weather_history
            ORDER BY searched_at DESC
        """)

        records = cursor.fetchall()
        cursor.close()
        connection.close()

        for record in records:
            record["searched_at"] = record["searched_at"].isoformat()

        return jsonify(records)

    except mysql.connector.Error:
        app.logger.exception("MySQL database error")
        return jsonify({"error": "Could not retrieve weather history."}), 500


@app.route("/api/forecast")
def get_forecast():
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    if not API_KEY:
        return jsonify({"error": "Weather API key is missing."}), 500

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )

        if response.status_code == 404:
            return jsonify({"error": "City not found."}), 404

        if response.status_code == 401:
            return jsonify({
                "error": "API key invalid hai ya forecast access ready nahi hai."
            }), 502

        response.raise_for_status()
        data = response.json()

        # Group 3-hour forecasts by date
        daily = {}

        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]
            temp = item["main"]["temp"]

            if date not in daily:
                daily[date] = {
                    "date": date,
                    "min": temp,
                    "max": temp,
                    "conditions": []
                }

            daily[date]["min"] = min(daily[date]["min"], temp)
            daily[date]["max"] = max(daily[date]["max"], temp)
            daily[date]["conditions"].append({
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            })

        forecast = []

        for day in list(daily.values())[:5]:
            # Use the condition nearest to midday, if available
            day_items = [
                item for item in data["list"]
                if item["dt_txt"].startswith(day["date"])
            ]
            chosen = min(
                day_items,
                key=lambda item: abs(
                    int(item["dt_txt"][11:13]) - 12
                )
            )
            weather = chosen["weather"][0]

            forecast.append({
                "date": day["date"],
                "min": round(day["min"]),
                "max": round(day["max"]),
                "condition": weather["description"].title(),
                "icon": weather["icon"]
            })

        return jsonify({
            "city": data["city"]["name"],
            "forecast": forecast
        })

    except requests.Timeout:
        return jsonify({"error": "Forecast service timed out."}), 504

    except requests.RequestException:
        return jsonify({"error": "Forecast service se connect nahi ho paaya."}), 502

    except (KeyError, IndexError, TypeError, ValueError):
        return jsonify({"error": "Unexpected forecast data received."}), 502

if __name__ == "__main__":
    app.run(debug=True, port=5000)
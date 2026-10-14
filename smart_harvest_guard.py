from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Harvest Guard</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f8ef;
            color: #24412b;
        }

        header {
            background: #245c35;
            color: white;
            padding: 20px 7%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin-left: 15px;
        }

        .hero {
            padding: 75px 8%;
            color: white;
            min-height: 340px;
            background:
                linear-gradient(90deg,
                rgba(13,48,24,.85),
                rgba(13,48,24,.2)),
                url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85")
                center/cover;
        }

        .hero h1 {
            font-size: clamp(32px, 5vw, 48px);
            max-width: 650px;
        }

        .hero p {
            max-width: 550px;
            line-height: 1.7;
        }

        .btn {
            background: #f4c95d;
            color: #24412b;
            padding: 12px 20px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-weight: bold;
        }

        main {
            max-width: 1150px;
            margin: auto;
            padding: 35px 20px;
        }

        .cards, .tips {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 22px 0 35px;
        }

        .card {
            background: white;
            padding: 23px;
            border-radius: 12px;
            box-shadow: 0 4px 15px #24412b12;
        }

        .card h3 {
            color: #315e37;
        }

        .value {
            font-size: 28px;
            font-weight: bold;
            color: #245c35;
        }

        .tip {
            background: #e4f0df;
            padding: 20px;
            border-radius: 10px;
        }

        input {
            padding: 12px;
            border: 1px solid #c8d8c4;
            border-radius: 7px;
            width: min(100%, 320px);
            font-size: 15px;
        }

        .notice {
            background: #fff5d8;
            padding: 20px;
            border-left: 5px solid #e5b333;
            border-radius: 7px;
        }

        .message {
            margin: 15px 0;
        }

        footer {
            background: #193f27;
            color: white;
            text-align: center;
            padding: 25px;
        }

        @media(max-width: 600px) {
            header {
                padding: 18px;
            }

            nav a {
                margin: 0 8px 0 0;
            }

            .hero {
                padding: 45px 6%;
            }
        }
    </style>
</head>

<body>

<header>
    <h2>🌾 Smart Harvest Guard</h2>
    <nav>
        <a href="#home">Home</a>
        <a href="#weather">Weather</a>
        <a href="#protection">Crop Protection</a>
    </nav>
</header>

<section class="hero" id="home">
    <h1>Protect Your Harvest, Secure Your Future</h1>
    <p>
        Monitor weather conditions, prepare for rainfall,
        and make informed decisions to protect your crops.
    </p>
    <a href="#weather">
        <button class="btn">Check Weather</button>
    </a>
</section>

<main>

<section id="weather">
    <h2>🌤 Weather Dashboard</h2>

    <form method="POST">
        <input
            type="text"
            name="location"
            placeholder="Enter your city or village"
            value="{{ location }}"
            required
        >
        <button class="btn" type="submit">Get Weather</button>
    </form>

    {% if message %}
        <p class="message" role="status">{{ message }}</p>
    {% endif %}

    <div class="cards">
        <div class="card">
            <h3>🌡️ Temperature</h3>
            <div class="value">{{ temperature }}</div>
            <p>Current air temperature</p>
        </div>

        <div class="card">
            <h3>🌧️ Rainfall Probability</h3>
            <div class="value">{{ rain }}</div>
            <p>Forecast for the current hour</p>
        </div>

        <div class="card">
            <h3>💧 Humidity</h3>
            <div class="value">{{ humidity }}</div>
            <p>Relative humidity</p>
        </div>

        <div class="card">
            <h3>🌬️ Wind Speed</h3>
            <div class="value">{{ wind }}</div>
            <p>Current wind conditions</p>
        </div>
    </div>

    <div class="notice">
        <h3>🛡️ Harvest Advisory</h3>
        <p>{{ advisory }}</p>
    </div>
</section>

<section id="protection">
    <h2>🌱 Crop Protection Tips</h2>

    <div class="tips">
        <div class="tip">
            <h3>🌧️ Before Rainfall</h3>
            <p>
                Protect harvested crops with covered storage
                and check field drainage.
            </p>
        </div>

        <div class="tip">
            <h3>☀️ During Dry Weather</h3>
            <p>
                Monitor soil moisture and plan irrigation
                according to crop requirements.
            </p>
        </div>

        <div class="tip">
            <h3>📦 Safe Storage</h3>
            <p>
                Store produce in a dry, ventilated place
                to reduce moisture damage.
            </p>
        </div>
    </div>
</section>

</main>

<footer>
    <p>🌾 Smart Harvest Guard</p>
    <p>Helping farmers make informed harvest decisions.</p>
</footer>

</body>
</html>
"""


def get_weather(location):
    try:
        # Find coordinates for the entered location.
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geo_url,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        geo_response.raise_for_status()

        results = geo_response.json().get("results", [])

        if not results:
            return None, "Location not found. Please try again."

        place = results[0]

        # Retrieve weather and hourly rainfall probability.
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_response = requests.get(
            weather_url,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "precipitation,wind_speed_10m"
                ),
                "hourly": "precipitation_probability",
                "forecast_days": 1,
                "timezone": "auto"
            },
            timeout=10
        )
        weather_response.raise_for_status()

        data = weather_response.json()
        current = data["current"]

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        probabilities = hourly.get("precipitation_probability", [])

        current_time = current["time"]
        index = next(
            (i for i, t in enumerate(times) if t >= current_time),
            None
        )

        rain_probability = (
            probabilities[index]
            if index is not None and index < len(probabilities)
            else None
        )

        advisory = (
            "Rain is likely in the selected forecast hour. "
            "Check the full forecast and protect harvested crops."
            if rain_probability is not None and rain_probability >= 60
            else
            "Check the complete local forecast before harvesting. "
            "Current conditions alone cannot guarantee dry weather."
        )

        return {
            "temperature": f'{current["temperature_2m"]} °C',
            "humidity": f'{current["relative_humidity_2m"]}%',
            "wind": f'{current["wind_speed_10m"]} km/h',
            "rain": (
                f"{rain_probability}%"
                if rain_probability is not None
                else "Unavailable"
            ),
            "advisory": advisory,
            "message": (
                f'Weather for {place["name"]}'
                + (
                    f', {place["admin1"]}'
                    if place.get("admin1")
                    else ""
                )
                + f' | Updated {current_time}'
            )
        }, None

    except requests.RequestException:
        return None, (
            "Unable to connect to the weather service. "
            "Check your internet connection and try again."
        )
    except (KeyError, ValueError, TypeError, IndexError):
        return None, "Weather data is unavailable. Please try again."


@app.route("/", methods=["GET", "POST"])
def home():
    location = ""
    message = ""
    temperature = "--"
    humidity = "--"
    wind = "--"
    rain = "--"
    advisory = "Enter your location to receive a weather advisory."

    if request.method == "POST":
        location = request.form.get("location", "").strip()

        if location:
            weather, error = get_weather(location)

            if error:
                message = error
            else:
                temperature = weather["temperature"]
                humidity = weather["humidity"]
                wind = weather["wind"]
                rain = weather["rain"]
                advisory = weather["advisory"]
                message = weather["message"]

    return render_template_string(
        HTML,
        location=location,
        message=message,
        temperature=temperature,
        humidity=humidity,
        wind=wind,
        rain=rain,
        advisory=advisory
    )


if __name__ == "__main__":
    app.run(debug=True)

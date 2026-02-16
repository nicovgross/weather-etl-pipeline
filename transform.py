import pandas as pd
import json

with open("weather_data.json", "r") as f:
    data_dict = json.load(f)

df_data = pd.DataFrame(data_dict)
df_data.rename(columns={
    "temperature_2m": "temperature_c",
    "apparent_temperature_2m": "apparent_temperature_c",
    "relative_humidity_2m": "relative_humidity_%",
    "precipitation_probability": "precipitation_probability_%" ,
    "precipitation": "precipitation_mm",
    "windspeed_10m": "windspeed_kmh",
    "winddirection_10m": "winddirection_deg",
    "weathercode": "weather_code", 
    "couldcover": "cloud_cover_%"
}, inplace=True)

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "LightRain showers",
    81: "Moderate rain shower",
    82: "Heavy rain shower",
    85: "Light snow shower",
    86: "Heavy snow shower",
    95: "Thunderstorm",
    96: "Thunderstorm with heavy hail",
    99: "Thunderstorm with heavy hail"
}

df_data["weather_description"] = df_data["weather_code"].map(WEATHER_CODE_MAP)


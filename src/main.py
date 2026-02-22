from extract import *
from transform import *
import json

with open("../config/cities.json", "r") as f:
    cities = json.load(f)

for city in cities:
    params = { #Define parameters
        "city": city["city"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation_probability",
                    "precipitation", "windspeed_10m", "winddirection_10m", "weathercode", "cloudcover"],
        "timezone": city["timezone"], # Local timezone based on your location
        "current_weather": True
    }

    extract_data(params)
    transform_data(params)
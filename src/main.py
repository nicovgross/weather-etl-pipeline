from extract import *
from transform import *
from load import *
import json

with open("config/cities.json", "r") as f:
    cities = json.load(f)

for city in cities:
    params = { #Define parameters
        "city_name": city["city_name"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation_probability",
                    "precipitation", "windspeed_10m", "winddirection_10m", "weathercode", "cloudcover"],
        "timezone": city["timezone"], # Local timezone based on your location
        "current_weather": True
    }

    raw_file_path = extract_data(params)
    hourly_path, daily_path = transform_data(raw_file_path, city["city_name"])
    load_data(hourly_path, daily_path)
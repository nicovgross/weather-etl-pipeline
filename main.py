from extract import *

# Coordinates for a location (e.g., Berlin, Germany)
latitude = -22
longitude = -43

params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation_probability",
                "precipitation", "windspeed_10m", "winddirection_10m", "weathercode", "cloudcover"],
    "timezone": "America/Sao_Paulo", # Local timezone based on your location
    "current_weather": True
}

extract(params)
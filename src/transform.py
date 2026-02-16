import pandas as pd
import json

#Open json file with the weather data extracted by extract.py
with open("../data/raw/weather_data.json", "r") as f:
    data_dict = json.load(f)

#Rename columns, detailing units of measurement
df_data = pd.DataFrame(data_dict)
df_data.rename(columns={
    "temperature_2m": "temperature_c",
    "apparent_temperature": "apparent_temperature_c",
    "relative_humidity_2m": "relative_humidity_%",
    "precipitation_probability": "precipitation_probability_%",
    "precipitation": "precipitation_mm",
    "windspeed_10m": "wind_speed_kmh",
    "winddirection_10m": "wind_direction_deg",
    "weathercode": "weather_code", 
    "cloudcover": "cloud_cover_%"
}, inplace=True)

#Add weather description based on weather code
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

#Format time column to datetime type, instead of string
df_data["time"] = pd.to_datetime(df_data["time"], format="%Y-%m-%dT%H:%M")

#Separate time column into different columns
df_data["year"] = df_data["time"].dt.year
df_data["month"] = df_data["time"].dt.month
df_data["day"] = df_data["time"].dt.day
df_data["hour"] = df_data["time"].dt.hour

print(df_data)
print("\n\n")

#Store the extracted data in a json file
df_data.to_json("../data/processed/processed_weather_data.json", orient="records", date_format="iso", indent=2)

with open("../data/processed/processed_weather_data.json", "r") as f:
    numseioq = json.load(f)

numseiquela = pd.DataFrame(numseioq)
print(numseiquela)

#Convert to excel file for visualization
df_data.to_excel("../data/Hourly_data.xlsx")
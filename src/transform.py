import pandas as pd
import os
import json

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

def validate_weather_data(df):
    #Check null values
    for column in df.columns:
        assert df[column].isnull().sum() == 0, f"There are null values in column {column}"

    #Assert there are no absurd values
    assert df["temperature_c"].between(-89.2, 56.7).all(), "Inconsistent temperature detected"
    assert df["apparent_temperature_c"].between(-89.2, 56.7).all(), "Inconsistent apparent temperature detected"
    assert df["relative_humidity_%"].between(0,100).all(), "Inconsistent relative humidity detected"
    assert df["precipitation_probability_%"].between(0,100).all(), "Inconsistent precipitation probability detected"
    assert df["precipitation_mm"].ge(0).all(), "Inconsistent precipitation detected"
    assert df["wind_speed_kmh"].between(0,408).all(), "Inconsistent wind speed detected detected"
    assert df["wind_direction_deg"].between(0,360).all(), "Inconsistent wind direction detected"
    assert df["weather_code"].isin(WEATHER_CODE_MAP.keys()).all(), "Inconsistent weather code detected"

def transform_data(city):
    #Open json file with the weather data extracted by extract.py
    with open(f"../data/raw/{city}/raw_weather.json", "r") as f:
        data_dict = json.load(f)

    hourly = data_dict["hourly"]

    #Rename columns, detailing units of measurement
    hourly_weather = pd.DataFrame(hourly)
    hourly_weather.rename(columns={
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
    hourly_weather["weather_description"] = hourly_weather["weather_code"].map(WEATHER_CODE_MAP)

    #Format time column to datetime type, instead of string
    hourly_weather["time"] = pd.to_datetime(hourly_weather["time"], format="%Y-%m-%dT%H:%M")
    hourly_weather = hourly_weather.sort_values("time").reset_index(drop=True) #Make sure all rows are oredered

    #Separate time column into different columns
    hourly_weather["year"] = hourly_weather["time"].dt.year
    hourly_weather["month"] = hourly_weather["time"].dt.month
    hourly_weather["day"] = hourly_weather["time"].dt.day
    hourly_weather["hour"] = hourly_weather["time"].dt.hour

    validate_weather_data(hourly_weather)

    #Make sure the file path already exist
    file_path = f"../data/processed/{city}/hourly_weather.json"
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)

    #Store the extracted data in a JSON file
    hourly_weather.to_json(file_path, orient="records", date_format="iso", indent=2)

    #Create aggregate dataframe with relevant metrics
    daily_weather = hourly_weather.set_index("time").resample("D").agg(
        avg_temp = ("temperature_c", "mean"),
        min_temp = ("temperature_c", "min"),
        max_temp = ("temperature_c", "max"),
        temp_range = ("temperature_c", lambda x: x.max() - x.min()),
        avg_app_temp = ("apparent_temperature_c", "mean"),
        avg_hum = ("relative_humidity_%", "mean"),
        avg_precipitation_prob = ("precipitation_probability_%", "mean"),
        total_precipitation = ("precipitation_mm", "sum"),
        max_wind_speed = ("wind_speed_kmh", "max")
    ).round(1).reset_index()

    #Store the aggregate data in a JSON file
    daily_weather.to_json(f"../data/processed/{city}/daily_weather.json", orient="records", date_format="iso", indent=2)
import requests
import pandas as pd
import json
from datetime import datetime

#gets index of current time in time list from the hourly data
def get_current_time_index(current_time_date, times):
    for i in range(len(times)):
        if current_time_date == times[i]:
            return i
        elif times[i] < current_time_date < times[i+1]:
            min_value = min(abs(current_time_date - times[i]), abs(current_time_date - times[i+1]))
            if min_value == abs(current_time_date - times[i]):
                return i
            else:
                return i+1
            
def print_weather_data(weather_data):
    for key, value in weather_data.items():
        print(f"{key}: {value}")

# Coordinates for a location (e.g., Berlin, Germany)
latitude = -22
longitude = -43

# Define the API endpoint and parameters
BASE_URL = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability"],
    "timezone": "America/Sao_Paulo", # Local timezone based on your location
    "current_weather": True
}

try:
    # Make the API call
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the JSON response into a Python dictionary
    data = response.json()
    with open("weather_data.json", "w") as f:
        json.dump(data, f, indent=2)

    format_date = "%Y-%m-%dT%H:%M"
    hourly_data = data["hourly"]
    times = [datetime.strptime(t, format_date) for t in hourly_data["time"]]

    current_time_str = data["current_weather"]["time"] #gets the current time
    current_time_date = datetime.strptime(current_time_str, format_date) #converts current time to datetime object
    time_index = get_current_time_index(current_time_date, times) 

    #gets the data relative to the current time
    weather_data = {}
    weather_data["Time"] = hourly_data["time"][time_index:]
    weather_data["Temperature"] = hourly_data["temperature_2m"][time_index:]
    weather_data["Humidity"] = hourly_data["relative_humidity_2m"][time_index:]
    weather_data["Precipitacion Probability"] = hourly_data["precipitation_probability"][time_index:]

    df_data = pd.DataFrame(weather_data)
    print(df_data)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
import requests
import json

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

    current_time = data["current_weather"]["time"] #gets the current time

    hourly_data = data["hourly"]
    time_index = hourly_data["time"].index(current_time)

    #gets the data relative to the current time
    temperature = hourly_data["temperature_2m"][time_index]
    humidity = hourly_data["relative_humidity_2m"][time_index]
    precipitacion_prob = hourly_data["precipitation_probability"][time_index]

    print(temperature)
    print(humidity)
    print(precipitacion_prob)



    '''print(f"Current Temperature: {current_weather['temperature']} °C")
    print(f"Current Wind Speed: {current_weather['windspeed']} km/h")
    print(f"Time: {current_weather['time']}")'''

    # You can also access hourly data
    # print(json.dumps(data["hourly"], indent=2))

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
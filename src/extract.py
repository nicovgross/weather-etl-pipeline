import requests
import json
from datetime import datetime

'''
This program extracts raw data from the Open-Meteo API, gets the hourly data 
from the current time onwards and stores it in a JSON file
'''

#Get index of current time in time list from the hourly data
def get_current_time_index(current_time_date, times):
    n = len(times)
    for i in range(n):
        if current_time_date == times[i]:
            return i
        elif times[i] < current_time_date < times[i+1] and i != n-1:
            min_value = min(abs(current_time_date - times[i]), abs(current_time_date - times[i+1]))
            if min_value == abs(current_time_date - times[i]):
                return i
            else:
                return i+1
            
def print_weather_data(weather_data):
    for key, value in weather_data.items():
        print(f"{key}: {value}")

#Define the API endpoint and parameters
BASE_URL = "https://api.open-meteo.com/v1/forecast"

#Extracts data from the Open-Meteo API based on the given parameters
def extract_data(params):
    try:
        #Make the API call
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        #Parse the JSON response into a Python dictionary
        data = response.json()

        #Convert time data from string to datetime object
        format_date = "%Y-%m-%dT%H:%M"
        raw_data = data["hourly"]
        times = [datetime.strptime(t, format_date) for t in raw_data["time"]]

        current_time_str = data["current_weather"]["time"] #gets the current time
        current_time_date = datetime.strptime(current_time_str, format_date) #converts current time to datetime object
        time_index = get_current_time_index(current_time_date, times) 

        #Get the data relative to the current time
        raw_weather = {}
        for key, value in raw_data.items():
            raw_weather[f"{key}"] = value[time_index:]

        #Store the extracted data in a JSON file
        with open("../data/raw/raw_weather.json", "w") as f:
            json.dump(raw_weather, f, indent=2)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
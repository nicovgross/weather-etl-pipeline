import requests
import json
import os
from datetime import datetime

'''
This program extracts raw data from the Open-Meteo API, 
gets the hourly data and stores it in a JSON file
'''
            
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
        date = data["current_weather"]["time"][:10] #Get current date

        #Make sure the file path already exist
        raw_file_path = f"../data/raw/{params['city']}/{date}.json"
        dir_path = os.path.dirname(raw_file_path)
        os.makedirs(dir_path, exist_ok=True)

        #Store the extracted data in a JSON file
        with open(raw_file_path, "w") as f:
            json.dump(data, f, indent=2)

        return raw_file_path

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
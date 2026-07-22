from extract import *
from transform import *
from load import *
import json
import logging
import sys

if len(sys.argv) == 1:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
elif len(sys.argv) > 1 and sys.argv[1] == "no-log": 
    pass
else: 
    print("Argument invalid")


with open("config/cities.json", "r") as f:
    cities = json.load(f)

logging.info("Starting pipeline")

total_records = 0
for city in cities:

    logging.info(f"Processing city: {city['city_name']}")

    try:
        params = { #Define parameters
            "city_name": city["city_name"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation_probability",
                        "precipitation", "windspeed_10m", "winddirection_10m", "weathercode", "cloudcover"],
            "timezone": city["timezone"], # Local timezone based on your location
            "current_weather": True
        }

        logging.info("  Extracting data from API...")
        raw_file_path, num_records = extract_data(params)
        logging.info(f"  {num_records} records extracted")
        total_records += num_records

        logging.info("  Transforming...")
        hourly_paths, daily_paths = transform_data(raw_file_path, city["city_name"])
        
        logging.info("  Loading into database...")
        for hourly, daily in zip(hourly_paths, daily_paths):
            load_data(hourly, daily)

    except Exception as e:
        logging.error(e)

logging.info(f"Total of {total_records} extracted")
logging.info("Pipeline finished")
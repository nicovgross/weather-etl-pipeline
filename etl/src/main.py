from extract import *
from transform import *
from load import *
import os
import boto3
import json
import logging

s3 = boto3.client("s3")

BUCKET = os.getenv("AWS_BUCKET_NAME")

def upload_file_s3(s3, local_path):
    s3_key = local_path.replace("/tmp/data/", "")

    s3.upload_file(
        Filename=local_path,
        Bucket=BUCKET,
        Key=s3_key
    )

    logging.info(f"Uploaded {s3_key} to s3 bucket")

def run_pipeline():
  
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

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

            # EXTRACTION
            logging.info("  Extracting data from API...")
            raw_file_path, num_records = extract_data(params)
            upload_file_s3(s3, raw_file_path)
            logging.info(f"  {num_records} records extracted")
            total_records += num_records

            #TRANSFORMATION
            logging.info("  Transforming...")
            hourly_paths, daily_paths = transform_data(raw_file_path, city["city_name"])

            #LOADING
            logging.info("  Loading into database...")
            for hourly, daily in zip(hourly_paths, daily_paths):
                load_data(hourly, daily)
                upload_file_s3(s3, hourly)
                upload_file_s3(s3, daily)

        except Exception:
            logging.exception(f"Error processing city {city['city_name']}")

    logging.info(f"Total of {total_records} records extracted")
    logging.info("Pipeline finished")

if __name__ == "__main__":
    run_pipeline()
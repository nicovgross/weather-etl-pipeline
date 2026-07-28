import psycopg2
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path, override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
#Connect to database
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
except Exception as e:
    logging.error(f"Error connecting to database: {e}")

conn.autocommit=True
cursor = conn.cursor()

try:
    #Create dimension table city
    cursor.execute("""CREATE TABLE IF NOT EXISTS dim_city(
                    city_id SERIAL PRIMARY KEY,
                    city_name TEXT NOT NULL,
                    city_display_name TEXT NOT NULL,
                    state TEXT,
                    state_display_name TEXT,
                    state_code CHAR(2)
                    country TEXT,
                    country_display_name TEXT,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    timezone TEXT,
                    CONSTRAINT unique_city UNIQUE (city_name, state, country));""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS hourly_weather(
                    time TIMESTAMP NOT NULL,
                    city_id INT REFERENCES dim_city(city_id),
                    temperature_c FLOAT,
                    apparent_temperature_c FLOAT,
                    relative_humidity_pct INT,
                    precipitation_probability_pct INT,
                    precipitation_mm FLOAT,
                    wind_speed_kmh FLOAT,
                    wind_direction_deg INT,
                    weather_code INT,
                    weather_description TEXT, 
                    cloud_cover_pct INT,
                    PRIMARY KEY (time, city_id));""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS daily_weather(
                    time TIMESTAMP NOT NULL,
                    city_id INT REFERENCES dim_city(city_id),
                    avg_temp FLOAT,
                    min_temp FLOAT,
                    max_temp FLOAT,
                    temp_range FLOAT,
                    avg_app_temp FLOAT,
                    avg_hum FLOAT,
                    avg_precipitation_prob FLOAT,
                    total_precipitation FLOAT,
                    max_wind_speed FLOAT,
                    PRIMARY KEY (time, city_id));""")
except Exception as e:
    logging.error(f"Error creating tables: {e}")

cursor.close()
conn.close()
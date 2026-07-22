import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

df_cities = pd.read_json("config/cities.json")

#Connect to database
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "weather_db"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432")
)

conn.autocommit=True
cursor = conn.cursor()

cities_insert_query = """INSERT INTO dim_city(
                        city_name,
                        city_display_name,
                        state,
                        state_display_name,
                        country,
                        country_display_name,
                        latitude,
                        longitude,
                        timezone)
                        VALUES %s
                        ON CONFLICT (city_name)
                        DO UPDATE SET
                            city_display_name = EXCLUDED.city_display_name,
                            state = EXCLUDED.state,
                            state_display_name = EXCLUDED.state_display_name,
                            country = EXCLUDED.country,
                            country_display_name = EXCLUDED.country_display_name,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            timezone = EXCLUDED.timezone;"""

cities_tuples = list(df_cities.itertuples(index=False, name=None))
try:
    execute_values(cursor, cities_insert_query, cities_tuples, page_size=1000) #inserts data in batches of 1000 rows
    rows = cursor.fetchall()
    logger.info(f"{len(rows)} cities processed successfully")

    for city in rows:
        logger.info(f"Processed city: {city[0]}")

except psycopg2.Error as e:
    logger.error(f"Error updating dim_city: {e}")


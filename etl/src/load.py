import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path, override=True)

def load_data(hourly_path, daily_path):
    df_hourly_weather = pd.read_parquet(hourly_path)
    df_daily_weather = pd.read_parquet(daily_path)

    #Connect to database
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    conn.autocommit=True
    cursor = conn.cursor()

    cursor.execute("SELECT city_id, city_name FROM dim_city;")
    rows = cursor.fetchall()

    city_map = {name: cid for cid, name in rows}

    #Substitute city_name column for city_id
    df_hourly_weather["city_id"] = df_hourly_weather["city_name"].map(city_map)
    df_hourly_weather.drop(columns=["city_name"], inplace=True)
    df_daily_weather["city_id"] = df_daily_weather["city_name"].map(city_map)
    df_daily_weather.drop(columns=["city_name"], inplace=True)
    
    #Make sure columns are in same order as insert query
    df_hourly_weather = df_hourly_weather[["time", "city_id", "temperature_c", "apparent_temperature_c", 
                                        "relative_humidity_pct", "precipitation_probability_pct", 
                                        "precipitation_mm", "wind_speed_kmh", "wind_direction_deg", 
                                        "weather_code", "weather_description",  "cloud_cover_pct"]]
    df_daily_weather = df_daily_weather[["time", "city_id", "avg_temp", "min_temp", "max_temp", 
                                        "temp_range", "avg_app_temp", "avg_hum", "avg_precipitation_prob", 
                                        "total_precipitation", "max_wind_speed" ]]
    
    hourly_insert_query = """INSERT INTO hourly_weather(
                        time,
                        city_id,
                        temperature_c,
                        apparent_temperature_c,
                        relative_humidity_pct,
                        precipitation_probability_pct,
                        precipitation_mm,
                        wind_speed_kmh,
                        wind_direction_deg,
                        weather_code,
                        weather_description, 
                        cloud_cover_pct)
                        VALUES %s
                        ON CONFLICT (time, city_id) DO NOTHING;
                    """

    hourly_tuples = list(df_hourly_weather.itertuples(index=False, name=None))
    execute_values(cursor, hourly_insert_query, hourly_tuples, page_size=1000) #inserts data in batches of 1000 rows

    daily_insert_query = """INSERT INTO daily_weather(
                    time,
                    city_id,
                    avg_temp,
                    min_temp,
                    max_temp,
                    temp_range,
                    avg_app_temp,
                    avg_hum,
                    avg_precipitation_prob,
                    total_precipitation,
                    max_wind_speed) 
                    VALUES %s
                    ON CONFLICT (time, city_id) DO NOTHING;
                """
    daily_tuples = list(df_daily_weather.itertuples(index=False, name=None))
    execute_values(cursor, daily_insert_query, daily_tuples, page_size=1000)

    cursor.close()
    conn.close()
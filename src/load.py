import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

df_hourly_weather = pd.read_parquet("../data/processed/hourly_weather.parquet")
df_daily_weather = pd.read_parquet("../data/processed/daily_weather.parquet")
df_cities = pd.read_json("../config/cities.json")

#Connect to database
conn = psycopg2.connect(
    dbname="weather_db",
    user="postgres",
    password="etl2026",
    host="localhost",
    port="5432"
)
conn.autocommit=True
cursor = conn.cursor()

cities_insert_query = """INSERT INTO dim_city(
                    city_name,
                    state,
                    country,
                    latitude,
                    longitude,
                    timezone)
                    VALUES %s
                    ON CONFLICT (city_name) DO NOTHING;"""

cities_tuples = list(df_cities.itertuples(index=False, name=None))
execute_values(cursor, cities_insert_query, cities_tuples, page_size=1000) #inserts data in batches of 1000 rows

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
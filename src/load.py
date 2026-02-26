import pandas as pd
import psycopg2

hourly_weather = pd.read_parquet("../data/processed/hourly_weather.parquet")
daily_weather = pd.read_parquet("../data/processed/daily_weather.parquet")

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

cursor.close()
conn.close()
import psycopg2

#Connect to database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="etl2026",
    host="localhost",
    port="5432"
)

conn.autocommit=True
cursor = conn.cursor()

cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("weather_db",))
exists = cursor.fetchone()
if not exists: 
    cursor.execute("CREATE DATABASE weather_db;") #Create database if it doesn't exist

cursor.close()
conn.close()

conn = psycopg2.connect(
    dbname="weather_db",
    user="postgres",
    password="etl2026",
    host="localhost",
    port="5432"
)

conn.autocommit=True
cursor = conn.cursor()

#Create dimension table city
cursor.execute("""CREATE TABLE IF NOT EXISTS dim_city(
                city_id SERIAL PRIMARY KEY,
                city_name TEXT NOT NULL,
                state TEXT,
                country TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                timezone TEXT);""")

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
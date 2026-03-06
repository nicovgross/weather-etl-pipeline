# Weather ETL Pipeline
This project implements an ETL pipeline that extracts, transforms and loads weather data. The goal of this project is to develop my skills in data engineering and data analysis and to deepen my understanding of data pipelines.

### Setup
The requirements for this project are detailed in requirements.txt. Run:
```bash
pip install -r requirements.txt
```

Before running main, create the PostgreSQL database and necessary tables:
```bash
python scripts/setup_database.py
``` 

You must also configure the following environment variables:
```bash
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
``` 
For windows use:
```bash
setx VARIABLE_NAME value
```
For linux:
```bash
export VARIABLE_NAME=value
```

## Extraction
The weather data is extracted from the Open-Meteo API, which is open-source and doesn't require a key. For every city in file config/cities.json, a request is sent to the API for the hourly data from today in that city. Then, the data is stored in Parquet files. The Parquet format was used instead of JSON to optimize storage and reduce query time. The pipeline retrieves the following data:

* temperature
* apparent temperature
* relative humidity
* precipitation probability
* precipitation
* wind speed
* wind direction
* weather code
* cloud cover

The extracted data is then stored in \data\raw.

## Transformation
For the transformation step, the extracted data is first standardized(renaming columns, converting time from string do datetime). Then it is normalized, correcting possible inconsistencies and checking missing data. A new column is added: weather description. At last the data is divided into two dataframes: 

* hourly_weather: Detailed hourly measurements for each city.
* daily_weather: Aggregated daily metrics, calculated using hourly_weather.

Then, the transformed data is partitioned in buckets of year and month and stored in \data\processed.

## Load
After transformation, the processed data is loaded into a PostgreSQL database. The database schema includes:

* dim_city: dimension table containing city metadata
* hourly_weather: hourly weather measurements
* daily_weather: aggregated daily weather statistics

Since the pipeline only loads data from that day, it doesn't process data that may have been in the data folder already. To load all the data inside the data folder into the database, run:
```bash
python scripts/load_all.py
``` 

## Dashboard
An interactive Streamlit dashboard was built to visualize the weather data stored in the database. It's very simple and it's meant to be temporary.

To run the dashboard:
```bash
streamlit run src/dashboard/app.py
```
<img width="993" height="738" alt="image" src="https://github.com/user-attachments/assets/795516c0-f334-4d3c-9689-da71f1875ee1" />

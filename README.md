# Weather ETL Pipeline
This project implements an end-to-end weather data platform. It automatically extracts weather data from the Open-Meteo API, transforms and validates the data, stores historical datasets in Amazon S3, loads processed data into Amazon RDS (PostgreSQL) and displays it through a Node.js web application.

The project was developed to strengthen my skills in Data Engineering, Cloud Computing, and Backend Development, covering the complete lifecycle of a production-ready data pipeline.

## Architecture
The pipeline follows the architecture below:

- Amazon EventBridge Scheduler triggers the pipeline every 6 hours.
- AWS Lambda runs the ETL pipeline inside a Docker container.
- Weather data is extracted from the Open-Meteo API.
- Raw and processed data are stored in Amazon S3 as a data lake.
- Processed data is loaded into an Amazon RDS PostgreSQL database.
- A Node.js/Express backend running on an Amazon EC2 instance queries the database.
- The frontend consumes the backend API and displays the weather information.

## Setup
Install dependencies for etl pipeline:
```bash
pip install -r etl/src/requirements.txt
```

Create the PostgreSQL database schema:
```bash
python etl/scripts/setup_database.py
```

Configure the following environment variables:
```bash
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
AWS_BUCKET_NAME

BASE_DIR
```

If you are executing the pipeline from a Lambda function, the AWS environment variables should automatically be setup by `boto3`

Run pipeline:
```bash
python etl/src/main.py
```

## ETL

### Extraction
The weather data is extracted from the Open-Meteo API, which is open-source and doesn't require a key. For every city in file `etl/config/cities.json`, a request is sent to the API for the hourly data from today in that city. Then, the data is stored in Parquet files inside `data/raw`. The raw files are then sent to the S3 bucket.

- temperature
- apparent temperature
- relative humidity
- precipitation probability
- precipitation
- wind speed
- wind direction
- weather code
- cloud cover

### Transformation
For the transformation step, the extracted data is first standardized(renaming columns, converting time from string do datetime). Then it is normalized, correcting possible inconsistencies and checking missing data. A new column is added: weather description. At last the data is divided into two dataframes: 
- hourly_weather: Detailed hourly measurements for each city.
- daily_weather: Aggregated daily metrics, calculated using hourly_weather.

Then, the transformed data is partitioned in buckets of year and month and stored in `data/processed`, also in the S3 bucket.

### Loading
After transformation, the processed data is loaded into a AWS RDS PostgreSQL database. The database schema includes:

- dim_city: dimension table containing city metadata
- hourly_weather: hourly weather measurements
- daily_weather: aggregated daily weather statistics

Since the pipeline only loads data from that day, it doesn't process data that may have been in the data folder already. To load all the data inside the data folder into the database, run:
```bash
python etl/scripts/load_all.py
``` 

## Database schema


## AWS Deployment
- The pipeline is containarized using Docker.
- The Docker image is loaded into Amazon ECR.
- A Lambda function is created using the image imported from ECR.
- EventBridge Scheduler executes the Lambda function every 6 hours feeding the PostgreSQL database.

Build Docker image:
```bash
docker buildx build --platform linux/amd64 --provenance=false --load -t weather-etl-pipeline .
```

Tag image to ECR repository:
```bash
docker tag weather-etl-pipeline:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repo_name>:latest
```

Push image to ECR:
```bash
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<repo_name>:latest
```

## Web Application
The web application is built with Node.js and Express and is deployed on an Amazon EC2 instance.

The backend:

- Connects to Amazon RDS
- Retrieves historical weather information
- Serves the frontend dashboard
- Runs continuously using PM2
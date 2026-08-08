# Weather ETL Pipeline
This project implements an end-to-end weather data platform. It automatically extracts weather data from the Open-Meteo API, transforms and validates the data, stores historical datasets in Amazon S3, loads processed data into Amazon RDS (PostgreSQL) and displays it through a Node.js web application.

The project was developed to strengthen my skills in Data Engineering, Cloud Computing, and Backend Development, covering the complete lifecycle of a production-ready data pipeline.

## Architecture
The pipeline follows the architecture below:

<img width="1497" height="392" alt="image" src="https://github.com/user-attachments/assets/4963931d-2309-40b9-a9bf-a6feb8c4d3cf" />

- Amazon EventBridge Scheduler triggers the pipeline every 6 hours.
- AWS Lambda runs the ETL pipeline inside a Docker container.
- Weather data is extracted from the Open-Meteo API.
- Raw and processed data are stored in Amazon S3 as a data lake.
- Processed data is loaded into an Amazon RDS PostgreSQL database.
- A Node.js/Express backend running on an Amazon EC2 instance queries the database.
- The frontend consumes the backend API and displays the weather information.

## Technologies

- Python
- Pandas
- PostgreSQL
- Docker
- AWS
- Node.js
- Express
- PM2

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

When executed on AWS Lambda, AWS credentials are automatically provided through the Lambda execution role. Therefore, AWS environment variables are only required for local execution.

Run pipeline:
```bash
python etl/src/main.py
```

## ETL

### Extraction
For every city listed in `etl/config/cities.json`, the pipeline requests hourly weather data from the Open-Meteo API. The extracted data is stored locally as Parquet files under `data/raw` and then uploaded to Amazon S3.

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
For the transformation step, the extracted data is first standardized(renaming columns, converting timestamps from strings to datetime objects. Then it is validated, correcting possible inconsistencies and checking missing data. A new column is added: weather description. At last the data is divided into two dataframes: 
- hourly_weather: Detailed hourly measurements for each city.
- daily_weather: Aggregated daily metrics, calculated using hourly_weather.

Then, the transformed data is partitioned in buckets of year and month and stored in `data/processed`, also in the S3 bucket.

### Loading
After transformation, the processed data is loaded into a AWS RDS PostgreSQL database. The database schema contains:

- dim_city: dimension table containing city metadata
- hourly_weather: hourly weather measurements
- daily_weather: aggregated daily weather statistics

Since the pipeline only loads data from that day, it doesn't process data that may have been in the data folder already. To load all the data inside the data folder into the database, run:
```bash
python etl/scripts/load_all.py
``` 

## Database schema
<img width="537" height="737" alt="image" src="https://github.com/user-attachments/assets/8c038a42-ea83-43e2-a9bf-25d12fd68ece" />

## AWS Deployment
- The pipeline is containarized using Docker.
- The Docker image is loaded into Amazon ECR.
- A Lambda function is created using the image imported from ECR.
- EventBridge Scheduler executes the Lambda function every 6 hours feeding the PostgreSQL database.

Login to AWS
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```

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
The web application is built with Node.js and Express and is hosted on an Amazon EC2 instance.

The backend:

- Connects to Amazon RDS
- Retrieves historical weather information
- Serves the frontend dashboard
- Runs continuously using PM2

## EC2 Setup
After connecting to the EC2 instance through SSH, install Node.js and npm according to the operating system being used.

Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

Install the Node.js dependencies:

```bash
npm install
```

## PM2
PM2 is used to keep the Node.js application running continuously and automatically restart it if the process stops.

Install PM2:

```bash
sudo npm install -g pm2
```

Start the application:

```bash
pm2 start index.js --name weather-app
```

Check the application status:

```bash
pm2 status
```

## Nginx
Nginx is used as a reverse proxy, forwarding public HTTP/HTTPS requests to the Node.js application running on port 3000.

Install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

Enable and start Nginx:

```bash
sudo systemctl enable --now nginx
```

Create the Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/dailyweather
```

Example configuration:
```
server {
    listen 80;
    server_name dailyweather.dev;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/dailyweather /etc/nginx/sites-enabled/
```

Remove the default configuration:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Test the Nginx configuration:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

## HTTPS
The application uses a .dev domain, which requires HTTPS.

Certbot and the Nginx plugin can be installed with:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

Generate and configure the SSL certificate:

```bash
sudo certbot --nginx -d dailyweather.dev
```

Certbot automatically configures the certificate and can redirect HTTP requests to HTTPS.

The application is then accessible at: https://dailyweather.dev

## Demo
<img width="1820" height="840" alt="image" src="https://github.com/user-attachments/assets/41cd877f-29e4-4711-b8c9-57f75278555f" />

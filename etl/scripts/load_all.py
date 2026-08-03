import os
from src.transform import transform_data
from src.load import load_data

raw = "data\\raw"
for city in os.listdir(raw):
    path = os.path.join(raw, city)
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        hourly_paths, daily_paths = transform_data(file_path, city["city_name"])

        for hourly, daily in zip(hourly_paths, daily_paths):
            load_data(hourly, daily)
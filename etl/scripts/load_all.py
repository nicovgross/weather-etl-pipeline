import os
from src.transform import transform_data
from src.load import load_data

raw = "data\\raw"
for city in os.listdir(raw):
    path = os.path.join(raw, city)
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        hourly_path, daily_path = transform_data(file_path, city)
        load_data(hourly_path, daily_path)
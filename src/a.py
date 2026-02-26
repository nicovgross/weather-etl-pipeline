import pandas as pd

df = pd.read_parquet("../data/processed/hourly_weather.parquet")
pd.set_option('display.max_columns', None)
print(df)
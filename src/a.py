import pandas as pd

path = "../data/processed/rio_de_janeiro/daily_weather.parquet"
df = pd.read_parquet(path)
print(df)
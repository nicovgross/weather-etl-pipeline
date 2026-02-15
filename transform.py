import pandas as pd
import json

with open("weather_data.json", "r") as f:
    data_dict = json.load(f)

df_data = pd.DataFrame(data_dict)
print(df_data)
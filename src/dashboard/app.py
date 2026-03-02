import streamlit as st
import pandas as pd
from db import get_engine

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("🌤 Weather Analytics Dashboard")

engine = get_engine()

@st.cache_data
def load_data():
    query = """
        SELECT time, city_id, temperature_c, precipitation_mm
        FROM hourly_weather
        ORDER BY time
    """
    return pd.read_sql(query, engine)

df = load_data()

# Sidebar filtro
cities = df["city_id"].unique()
selected_city = st.sidebar.selectbox("Select city", cities)

filtered_df = df[df["city_id"] == selected_city]

st.subheader(f"Temperature Over Time — {selected_city}")

st.line_chart(
    filtered_df.set_index("time")["temperature_c"]
)

st.subheader("Precipitation")

st.bar_chart(
    filtered_df.set_index("time")["precipitation_mm"]
)
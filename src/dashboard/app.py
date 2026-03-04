import streamlit as st
import pandas as pd
from db_config import get_engine

st.set_page_config(page_title="Weather Dashboard", layout="wide")

st.title("Weather Forecast")

engine = get_engine()

# ==========================
# QUERIES
# ==========================

hourly_query = """
    SELECT 
        time,
        c.city_name,
        temperature_c,
        apparent_temperature_c,
        relative_humidity_pct,
        precipitation_mm,
        precipitation_probability_pct,
        wind_speed_kmh,
        weather_description
    FROM hourly_weather h INNER JOIN dim_city c ON h.city_id = c.city_id 
    ORDER BY time
"""

hourly = pd.read_sql(hourly_query, engine)

# ==========================
# SIDEBAR
# ==========================
CITY_DISPLAY_MAP = {
    "rio_de_janeiro": "Rio de Janeiro",
    "sao_paulo": "São Paulo"
}
def format_city_name(city):
    return CITY_DISPLAY_MAP.get(city, city.replace("_", " ").title())

cities = hourly["city_name"].unique()

city_display = {c: format_city_name(c) for c in cities}

selected_display = st.sidebar.selectbox(
    "Select city",
    options=list(city_display.values())
)

# recuperar o valor real
selected_city = [
    key for key, value in city_display.items()
    if value == selected_display
][0]

filtered_df = hourly[hourly["city_name"] == selected_city].copy()
filtered_df = filtered_df.sort_values("time")

# ==========================
# CURRENT WEATHER
# ==========================

latest = filtered_df.iloc[-1]

WEATHER_EMOJI = {
    "Clear sky": "☀️",
    "Mainly clear": "🌤",
    "Partly cloudy": "⛅",
    "Overcast": "☁️",
    "Fog": "🌫",
    "Light rain": "🌦",
    "Moderate rain": "🌧",
    "Heavy rain": "🌧",
    "Thunderstorm": "⛈",
    "Light snow": "🌨",
    "Moderate snow": "🌨",
    "Heavy snow": "❄️"
}

emoji = WEATHER_EMOJI.get(latest["weather_description"], "🌍")

# Layout superior
col1, col2 = st.columns([2, 3])
hourly["time"] = pd.to_datetime(hourly["time"])

with col1:
    # Formatar data
    formatted_date = latest["time"].strftime("%d %B %Y - %H:%M")
    
    st.markdown(f"##### {formatted_date}")
    st.markdown(f"# {round(latest['temperature_c'])}°C")
    st.markdown(f"### {latest['weather_description']} {emoji}")

with col2:
    st.metric("Humidity", f"{latest['relative_humidity_pct']}%")
    st.metric("Apparent Temp", f"{round(latest['apparent_temperature_c'])}°C")
    st.metric("Wind Speed", f"{latest['wind_speed_kmh']} km/h")
    st.metric("Precipitation Prob.", f"{latest['precipitation_probability_pct']}%")

st.divider()

# ==========================
# HISTORICAL SECTION
# ==========================

st.subheader("Temperature (°C)")
st.line_chart(
    filtered_df.set_index("time")["temperature_c"]
)

st.subheader("Precipitation (mm)")
st.bar_chart(
    filtered_df.set_index("time")["precipitation_mm"]
)
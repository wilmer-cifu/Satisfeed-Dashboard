import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="Satisfeed Dashboard", layout="wide")

st.title("Georgia Schools Dashboard 🗺️")
st.write("Click a school to see details")

# Load data
df = pd.read_csv("dashboard_data_geocoded.csv")

# Drop missing coordinates
df = df.dropna(subset=["LAT", "LON"])

# Create map centered on Georgia
m = folium.Map(location=[32.7, -83.3], zoom_start=7)

marker_cluster = MarkerCluster().add_to(m)

# Add markers
for _, row in df.iterrows():
    popup = f"""
    <b>School:</b> {row['SCHOOLNAME']}<br>
    <b>Address:</b> {row['STREET']}, {row['CITY']}, {row['STATE']} {row['ZIP_CODE']}<br>
    <b>Grades:</b> {row['GRADES']}<br>
    <b>Score:</b> {row['SINGLESCORE']}
    """

    folium.Marker(
        location=[row["LAT"], row["LON"]],
        popup=popup,
        tooltip=row["SCHOOLNAME"]
    ).add_to(marker_cluster)

# Show map
st_folium(m, width=1200, height=700)
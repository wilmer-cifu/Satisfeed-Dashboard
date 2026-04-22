import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Satisfeed Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# Sidebar (Directory)
# -------------------------------
st.sidebar.title("Directory")
page = st.sidebar.radio("", ["Home", "Analysis", "Map"])

# -------------------------------
# Load Data
# -------------------------------
df = pd.read_csv("dashboard_data_geocoded.csv")

# -------------------------------
# HOME TAB
# -------------------------------
if page == "Home":
    st.title("Satisfeed Dashboard")

    st.markdown("**By: Wilmer Cifuentes, Ethan Boderas, Jaylan Igbinoba**")

    st.markdown("""
    ### Introduction
    This project focuses on building and maintaining a data-driven dashboard for Satisfeed, a food bank that serves up to 56,000 families. 

    The primary goal is to update the dashboard with new and relevant data and analyze data to generate meaningful statistics that support planning, reporting, and decision-making.

    We use Python and data science techniques to enable reliable data management, insightful analytics, and clear visualization of the food bank’s reach and effectiveness.
    """)

# -------------------------------
# ANALYSIS TAB
# -------------------------------
elif page == "Analysis":
    st.title("Analysis")

    # Jaylan
    st.subheader("Jaylan's Findings")
    st.image("Jaylan1.png", use_column_width=True)

    st.write("""
    The test that I have done showed that there is no correlation between the two variables. 
    The values lie between -2 and 2, meaning there is no strong negative or positive trend.

    The second graph also shows no upward or downward trend based on population, confirming no correlation.
    """)

    # Ethan
    st.subheader("Ethan's Findings")
    st.image("Ethan1.png", use_column_width=True)

    st.write("""
    Based on the k-means graph, the hypothesis is not strongly supported.

    Cluster 0 shows high free & reduced lunch percentages but varying student counts.
    Cluster 1 shows lower percentages across a wide range.
    Cluster 2 includes larger schools but does not follow a consistent trend.

    This suggests no direct correlation between student count and free & reduced lunch percentage.
    """)

    st.image("Ethan2.png", use_column_width=True)

    st.write("""
    The left graph shows most schools have high free & reduced lunch percentages.
    The right graph shows most schools have smaller student populations.
    """)

    st.image("Ethan3.png", use_column_width=True)

    st.write("""
    There is a clear relationship between poverty (free/reduced lunch) and SAT scores.
    Higher poverty levels are associated with lower SAT performance.
    """)

    # Wilmer
    st.subheader("Wilmer's Findings")
    st.image("Wilmer1.png", use_column_width=True)
    st.image("Wilmer2.png", use_column_width=True)

    st.write("""
    PCA results show the first component explains about 77% of the variance.

    This indicates child food insecurity and poverty-related variables are strongly related.
    """)

    st.image("Wilmer3.png", use_column_width=True)

    st.write("""
    The distribution shows child food insecurity is fairly spread out, while poverty levels are skewed higher.

    This means many counties have high levels of low-income households, helping explain food insecurity patterns.
    """)

# -------------------------------
# MAP TAB
# -------------------------------
elif page == "Map":
    st.title("Georgia Schools Map")

    # Create map centered on Georgia
    m = folium.Map(location=[33.95, -83.38], zoom_start=7)

    selected_school = None

    for _, row in df.iterrows():
        popup_text = f"{row.get('School Name', 'N/A')}"

        folium.Marker(
            location=[row["LAT"], row["LON"]],
            tooltip=popup_text
        ).add_to(m)

    # Display map
    map_data = st_folium(m, width=900, height=600)

    # Right side info panel
    st.subheader("Selected School Info")

    if map_data["last_object_clicked"]:
        lat = map_data["last_object_clicked"]["lat"]
        lon = map_data["last_object_clicked"]["lng"]

        selected = df[(df["LAT"] == lat) & (df["LON"] == lon)]

        if not selected.empty:
            school = selected.iloc[0]

            st.write(f"**School Name:** {school.get('School Name', 'N/A')}")
            st.write(f"**Address:** {school.get('FULL_ADDRESS', 'N/A')}")
            st.write(f"**Grade Level:** {school.get('Grade Level', 'N/A')}")
            st.write(f"**Single Score:** {school.get('Single Score', 'N/A')}")
            st.write(f"**Poverty Level:** {school.get('Poverty Level', 'N/A')}")
    else:
        st.write("Click on a school marker to see details.")
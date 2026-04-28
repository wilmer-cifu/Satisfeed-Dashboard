import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Satisfeed Dashboard",
    layout="wide"
)

# Helpers
def safe_image(path: str, width: int = 950):
    try:
        st.image(path, width=width)
    except Exception:
        st.warning(f"Could not load image: {path}")

def normalize_county_name(name):
    if pd.isna(name):
        return None
    name = str(name).strip()
    if name.lower().endswith(" county"):
        name = name[:-7].strip()
    return name.lower()

def fmt_pct(value):
    if pd.isna(value):
        return "N/A"
    try:
        value = float(value)
        if value <= 1:
            return f"{value:.1%}"
        return f"{value:.1f}%"
    except Exception:
        return str(value)

def insecurity_color(rate):
    try:
        rate = float(rate)
    except Exception:
        return "gray"

    if rate < 0.15:
        return "green"
    elif rate < 0.25:
        return "orange"
    else:
        return "red"

def insecurity_fill(rate):
    try:
        rate = float(rate)
    except Exception:
        return "#808080"

    if rate < 0.15:
        return "#2ecc71"
    elif rate < 0.25:
        return "#f39c12"
    else:
        return "#e74c3c"

def section_card(title: str):
    st.markdown(f"### {title}")

# School data
school_df = pd.read_csv("dashboard_data_geocoded.csv")

school_df["LAT"] = pd.to_numeric(school_df["LAT"], errors="coerce")
school_df["LON"] = pd.to_numeric(school_df["LON"], errors="coerce")
school_df = school_df.dropna(subset=["LAT", "LON"]).copy()

school_df["FULL_ADDRESS"] = (
    school_df["STREET"].fillna("").astype(str) + ", " +
    school_df["CITY"].fillna("").astype(str) + ", " +
    school_df["STATE"].fillna("").astype(str) + " " +
    school_df["ZIP_CODE"].fillna("").astype(str)
)

school_df["county_key"] = school_df["SYSTEMNAME"].apply(normalize_county_name)

# Feeding America data
fa_df = pd.read_excel("Feeding_America_Cleaned.xlsx")

fa_df["county_key"] = (
    fa_df["County, State"]
    .astype(str)
    .str.replace(", Georgia", "", regex=False)
    .str.replace(", GA", "", regex=False)
    .str.replace(" County", "", regex=False)
    .str.strip()
    .str.lower()
)

fa_keep = [
    "county_key",
    "Child Food Insecurity Rate",
    "# of Food Insecure Children",
    "% food insecure children in HH w/ HH incomes below 185 FPL",
    "% food insecure children in HH w/ HH incomes above 185 FPL",
]

fa_df = fa_df[fa_keep].drop_duplicates(subset=["county_key"])
df = school_df.merge(fa_df, on="county_key", how="left")

# Deployment
df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
df = df.dropna(subset=["LAT", "LON"]).copy()

# Directory
st.sidebar.title("Directory")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Analysis", "Map", "Data Overview"],
    label_visibility="collapsed"
)

# Home Page
if page == "Home":

    spacer_left, header_col, spacer_right = st.columns([0.3, 8, 0.3])

    with header_col:
        st.markdown(
            "<h1 style='text-align:center; margin-bottom: 0;'>Satisfeed Dashboard</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center; font-weight:600;'>By: Wilmer Cifuentes, Ethan Boderas, Jaylan Igbinoba</p>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center; font-weight:500;'>Client: Tim Turner | "
            "<a href='https://www.satisfeed.org/' target='_blank'>https://www.satisfeed.org/</a></p>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            ### Introduction
            This project focuses on building and maintaining a data-driven dashboard for Satisfeed, a food bank that serves up to 56,000 families. The primary goal is to update the dashboard with new and relevant data and analyze data to generate meaningful statistics that support planning, reporting, and decision-making.

            We will use Jupyter Notebook and Python to enable reliable data management, insightful analytics, and clear visualization of the food bank’s reach and effectiveness.
            """
        )

        st.markdown("###")

        img_left, img_center, img_right = st.columns([1, 2.2, 1])

        with img_center:
            st.image("Satisfeed1.png", width=700)

# Analysis Section
elif page == "Analysis":
    st.title("Analysis")

    st.subheader("Jaylan's Findings")
    safe_image("Jaylan1.png", width=950)
    st.write(
        """
        The test that I have done showed that there is no correlation between the two variables. You can see this in the 1st graph because the values lie in the -2 to 2 range, which typically means that the data does not lean very hard into a negative or positive trend. The second graph showed that the data also does not have an upwards or downwards trend based on population. This also means there is no correlation between the two variables.
        """
    )

    st.subheader("Ethan's Findings")
    safe_image("Ethan1.png", width=950)
    st.write(
        """
        Based on the k-means graph, the hypothesis does not seem to be strongly supported. Cluster 0 has a very high percentage of free & reduced lunch; however, their student count varies. This contradicts the idea that schools with higher populations will have higher percentages. Cluster 1 has a lower percentage of free & reduced lunch, but it also covers a broad spectrum. Finally, cluster 2 spans from a low to a high percentage of free & reduced lunch; however, these schools generally have higher student counts than the other clusters. This observation directly contradicts the hypothesis.

        This clustering suggests that the percentage of free & reduced lunch is not directly or positively correlated with the student count, and that any slight correlation indicates that smaller schools tend to have a higher free & reduced lunch percentage.
        """
    )

    safe_image("Ethan2.png", width=950)
    st.write(
        """
        The two graphs above were made to better display the distributions of the original features used for the clustering. The graph on the left shows that most schools have a high percentage of students eligible for free & reduced lunch. The graph on the right shows that the majority of schools have relatively small student counts, with the frequency of larger schools decreasing significantly.
        """
    )

    safe_image("Ethan3.png", width=950)
    st.write(
        """
        This shows a clear correlation between the percentage of students receiving free or reduced-price lunch and SAT scores. This indicates that schools where more students qualify for free or reduced-price lunch due to poverty have lower average SAT scores in both ELA and Math.
        """
    )

    st.subheader("Wilmer's Findings")
    safe_image("Wilmer1.png", width=950)
    safe_image("Wilmer2.png", width=950)
    st.write(
        """
        The PCA results show that the first component explains about 77% of the variance, which means most of the information in the data is captured in that one component. This tells me that child food insecurity and poverty related variables are pretty closely related.
        """
    )

    safe_image("Wilmer3.png", width=950)
    st.write(
        """
        The distribution plots show that child food insecurity is kind of spread out in a normal way while the percentage of children below 185% FPL is more skewed toward higher values. This means a lot of counties have a high number of kids in lower income households, which helps explain why food insecurity is an issue in those areas.
        """
    )

# Map
elif page == "Map":
    st.title("Georgia Schools Map")

    col_map, col_info = st.columns([2.2, 1])

    with col_map:
        m = folium.Map(
            location=[32.9, -83.4],
            zoom_start=7,
            tiles="CartoDB positron"
        )

        marker_cluster = MarkerCluster(
            name="Schools",
            disableClusteringAtZoom=12,
            spiderfyOnMaxZoom=True,
            showCoverageOnHover=False,
            zoomToBoundsOnClick=True
        ).add_to(m)

        for _, row in df.iterrows():
            lat = row.get("LAT")
            lon = row.get("LON")

            if pd.isna(lat) or pd.isna(lon):
                continue

            school_name = row.get("SCHOOLNAME", "School")
            insecurity_rate = row.get("Child Food Insecurity Rate", None)

            tooltip_text = school_name
            if pd.notna(insecurity_rate):
                tooltip_text += f" | Food Insecurity: {float(insecurity_rate):.1%}"

            folium.CircleMarker(
                location=[float(lat), float(lon)],
                radius=7,
                color=insecurity_color(insecurity_rate),
                weight=2,
                fill=True,
                fill_color=insecurity_fill(insecurity_rate),
                fill_opacity=0.9,
                tooltip=tooltip_text
            ).add_to(marker_cluster)

        legend_html = """
        <div style="
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 190px;
            z-index: 9999;
            font-size: 14px;
            background-color: rgba(20, 20, 20, 0.92);
            color: white;
            border-radius: 10px;
            padding: 12px 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        ">
            <div style="font-weight: 700; color: #2da8ff; margin-bottom: 8px;">
                FOOD INSECURITY
            </div>
            <div style="margin-bottom: 4px;">
                <span style="color:#2ecc71; font-size:16px;">●</span> &lt; 15% Low
            </div>
            <div style="margin-bottom: 4px;">
                <span style="color:#f39c12; font-size:16px;">●</span> 15%–24.9% Mid
            </div>
            <div>
                <span style="color:#e74c3c; font-size:16px;">●</span> ≥ 25% High
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        map_data = st_folium(m, width=920, height=680)

    with col_info:
        st.subheader("Selected School Info")

        clicked = map_data.get("last_object_clicked") if map_data else None

        if clicked:
            clicked_lat = clicked.get("lat")
            clicked_lon = clicked.get("lng")

            temp_df = df.copy()
            temp_df["distance"] = (
                (temp_df["LAT"] - clicked_lat) ** 2 +
                (temp_df["LON"] - clicked_lon) ** 2
            )

            school = temp_df.loc[temp_df["distance"].idxmin()]

            section_card("Basic Info")
            st.markdown(f"**School Name:** {school.get('SCHOOLNAME', 'N/A')}")
            st.markdown(f"**School Address:** {school.get('FULL_ADDRESS', 'N/A')}")
            st.markdown(f"**Grade Level:** {school.get('GRADES', 'N/A')}")
            st.markdown(f"**Single Score:** {school.get('SINGLESCORE', 'N/A')}")
            st.markdown(f"**County / System:** {school.get('SYSTEMNAME', 'N/A')}")

            st.markdown("---")
            section_card("Demographics")
            st.markdown(f"**% Asian:** {fmt_pct(school.get('PCT_ASIAN', None))}")
            st.markdown(f"**% Native:** {fmt_pct(school.get('PCT_NATIVE', None))}")
            st.markdown(f"**% Black:** {fmt_pct(school.get('PCT_BLACK', None))}")
            st.markdown(f"**% Hispanic:** {fmt_pct(school.get('PCT_HISPANIC', None))}")
            st.markdown(f"**% Multi:** {fmt_pct(school.get('PCT_MULTI', None))}")
            st.markdown(f"**% White:** {fmt_pct(school.get('PCT_WHITE', None))}")

            st.markdown("---")
            section_card("Academic Performance")
            st.markdown(f"**Content Mastery Elementary:** {fmt_pct(school.get('CONTENT_MASTERYE', None))}")
            st.markdown(f"**Content Mastery Middle School:** {fmt_pct(school.get('CONTENT_MASTERYM', None))}")
            st.markdown(f"**Content Mastery High School:** {fmt_pct(school.get('CONTENT_MASTERYH', None))}")
            st.markdown(f"**% Free & Reduced Lunch:** {fmt_pct(school.get('Percentage of Free & Reduced', None))}")
            st.markdown(f"**SAT Reading and Writing:** {school.get('SAT Reading and Writing', 'N/A')}")
            st.markdown(f"**SAT Math:** {school.get('SAT Math', 'N/A')}")

            st.markdown("---")
            section_card("County Poverty / Food Insecurity")

            child_rate = school.get("Child Food Insecurity Rate", None)
            food_insecure_children = school.get("# of Food Insecure Children", None)
            below_185 = school.get("% food insecure children in HH w/ HH incomes below 185 FPL", None)
            above_185 = school.get("% food insecure children in HH w/ HH incomes above 185 FPL", None)

            if pd.notna(child_rate):
                st.markdown(f"**Child Food Insecurity Rate:** {child_rate:.1%}")
            else:
                st.markdown("**Child Food Insecurity Rate:** N/A")

            if pd.notna(food_insecure_children):
                st.markdown(f"**# of Food Insecure Children:** {int(food_insecure_children):,}")
            else:
                st.markdown("**# of Food Insecure Children:** N/A")

            if pd.notna(below_185):
                st.markdown(f"**% in HH below 185% FPL:** {below_185:.1%}")
            else:
                st.markdown("**% in HH below 185% FPL:** N/A")

            if pd.notna(above_185):
                st.markdown(f"**% in HH above 185% FPL:** {above_185:.1%}")
            else:
                st.markdown("**% in HH above 185% FPL:** N/A")

        else:
            st.write("Click on an individual school node to see details.")
            st.write("If schools are clustered together, click the cluster to zoom in.")

# Data Overview
elif page == "Data Overview":
    st.title("Datasets")

    st.markdown("### Feeding America")
    st.markdown("[https://map.feedingamerica.org/](https://map.feedingamerica.org/)")
    st.write(
        """
        This dataset provides county level data about child food insecurity across Georgia. 
        The main fields used in this project include Child Food Insecurity Rate, number of food insecure children, 
        and the percentage of food insecure children in households below and above 185% of the Federal Poverty Level.
        """
    )

    st.markdown("---")

    st.markdown("### SAT Scores, Grades and Schools")
    st.markdown("[https://gosa.georgia.gov/dashboards-data-report-card/downloadable-data](https://gosa.georgia.gov/dashboards-data-report-card/downloadable-data)")
    st.write(
        """
        This dataset provides school level data from Georgia, including school names, addresses, grade levels, 
        demographics, content mastery scores, free and reduced lunch percentages, and SAT Reading/Writing and Math scores. 
        It was used to connect school performance and demographic data with county level food insecurity information.
        """
    )

    st.markdown("---")

    st.markdown("### Dataset Processing Summary")
    st.write(
        f"""
        The school dataset contains **{len(school_df):,} school records** after removing rows without valid latitude and longitude values. 
        The Feeding America dataset was cleaned by standardizing county names so it could be merged with the school data. 
        The final dashboard dataset connects each school to county level food insecurity indicators when a matching county is available.
        """
    )

    st.markdown("### Key Columns Used")
    st.write(
        """
        **School data columns:** SCHOOLNAME, STREET, CITY, STATE, ZIP_CODE, GRADES, SINGLESCORE, 
        PCT_ASIAN, PCT_NATIVE, PCT_BLACK, PCT_HISPANIC, PCT_MULTI, PCT_WHITE, 
        CONTENT_MASTERYE, CONTENT_MASTERYM, CONTENT_MASTERYH, Percentage of Free & Reduced, 
        SAT Reading and Writing, SAT Math.

        **Feeding America columns:** Child Food Insecurity Rate, # of Food Insecure Children, 
        % food insecure children in HH w/ HH incomes below 185 FPL, 
        % food insecure children in HH w/ HH incomes above 185 FPL.
        """
    )
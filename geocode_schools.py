import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

print("Loading CSV...")
df = pd.read_csv("dashboard data.csv")
print(f"Rows loaded: {len(df)}")

# test on first 20 rows only
df = df.head(20).copy()
print(f"Testing with {len(df)} rows")

df["FULL_ADDRESS"] = (
    df["STREET"].fillna("").astype(str) + ", " +
    df["CITY"].fillna("").astype(str) + ", " +
    df["STATE"].fillna("").astype(str) + " " +
    df["ZIP_CODE"].fillna("").astype(str)
)

geolocator = Nominatim(user_agent="satisfeed_school_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_location(address):
    try:
        location = geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

latitudes = []
longitudes = []

for i, address in enumerate(df["FULL_ADDRESS"], start=1):
    print(f"Processing {i}/{len(df)}: {address}")
    lat, lon = get_location(address)
    latitudes.append(lat)
    longitudes.append(lon)

df["LAT"] = latitudes
df["LON"] = longitudes

print("Saving file...")
df.to_csv("dashboard_data_geocoded.csv", index=False)
print("Done. Saved as dashboard_data_geocoded.csv")
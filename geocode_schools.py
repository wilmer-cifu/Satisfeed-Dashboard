import os
import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

RAW_FILE = "dashboard data.csv"
OUTPUT_FILE = "dashboard_data_geocoded.csv"

def build_full_address(df: pd.DataFrame) -> pd.Series:
    return (
        df["STREET"].fillna("").astype(str).str.strip() + ", " +
        df["CITY"].fillna("").astype(str).str.strip() + ", " +
        df["STATE"].fillna("").astype(str).str.strip() + " " +
        df["ZIP_CODE"].fillna("").astype(str).str.strip()
    ).str.strip()

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    if "FULL_ADDRESS" not in df.columns:
        df["FULL_ADDRESS"] = build_full_address(df)
    if "LAT" not in df.columns:
        df["LAT"] = pd.NA
    if "LON" not in df.columns:
        df["LON"] = pd.NA
    if "GEOCODE_STATUS" not in df.columns:
        df["GEOCODE_STATUS"] = pd.NA
    if "GEOCODED_AT" not in df.columns:
        df["GEOCODED_AT"] = pd.NA
    return df

def format_seconds(seconds: float) -> str:
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def main():
    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"Could not find {RAW_FILE}")

    raw_df = pd.read_csv(RAW_FILE)
    raw_df = ensure_columns(raw_df)

    print(f"Loaded raw dataset with {len(raw_df)} schools.")

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)
        old_df = ensure_columns(old_df)
        print(f"Found existing {OUTPUT_FILE} with {len(old_df)} rows. Merging saved progress...")

        # Keep only one saved result per address to avoid duplicate-index errors
        old_df_dedup = old_df.drop_duplicates(subset=["FULL_ADDRESS"], keep="last").copy()

        merge_cols = ["FULL_ADDRESS", "LAT", "LON", "GEOCODE_STATUS", "GEOCODED_AT"]
        raw_df = raw_df.merge(
            old_df_dedup[merge_cols],
            on="FULL_ADDRESS",
            how="left",
            suffixes=("", "_saved")
        )

        for col in ["LAT", "LON", "GEOCODE_STATUS", "GEOCODED_AT"]:
            saved_col = f"{col}_saved"
            raw_df[col] = raw_df[col].combine_first(raw_df[saved_col])
            raw_df.drop(columns=[saved_col], inplace=True)

    else:
        print(f"No existing {OUTPUT_FILE} found. Starting fresh...")

    df = raw_df.copy()

    geolocator = Nominatim(user_agent="satisfeed_school_mapper_full_run")
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,
        swallow_exceptions=True
    )

    total_rows = len(df)
    pending_mask = df["LAT"].isna() | df["LON"].isna()
    pending_indices = df.index[pending_mask].tolist()
    completed = total_rows - len(pending_indices)

    print(f"Total schools: {total_rows}")
    print(f"Already completed: {completed}")
    print(f"Remaining: {len(pending_indices)}")

    if not pending_indices:
        print("All schools are already geocoded.")
        df.to_csv(OUTPUT_FILE, index=False)
        return

    start_time = time.time()
    processed_this_run = 0

    for idx in pending_indices:
        row = df.loc[idx]
        address = str(row["FULL_ADDRESS"]).strip()

        if not address or address == ",":
            df.at[idx, "GEOCODE_STATUS"] = "missing_address"
            df.at[idx, "GEOCODED_AT"] = pd.Timestamp.now()
            df.to_csv(OUTPUT_FILE, index=False)
            continue

        print("-" * 70)
        print(f"Processing row {idx} | {completed + processed_this_run + 1}/{total_rows}")
        print(f"Address: {address}")

        row_start = time.time()
        location = geocode(address)

        if location:
            df.at[idx, "LAT"] = location.latitude
            df.at[idx, "LON"] = location.longitude
            df.at[idx, "GEOCODE_STATUS"] = "success"
            print(f"LAT: {location.latitude}, LON: {location.longitude}")
        else:
            df.at[idx, "GEOCODE_STATUS"] = "not_found"
            print("No match found.")

        df.at[idx, "GEOCODED_AT"] = pd.Timestamp.now()

        # Save progress after every row
        df.to_csv(OUTPUT_FILE, index=False)

        processed_this_run += 1
        elapsed = time.time() - start_time
        avg_per_school = elapsed / processed_this_run
        remaining = len(pending_indices) - processed_this_run
        eta = remaining * avg_per_school
        row_elapsed = time.time() - row_start

        print(f"Row time: {row_elapsed:.2f}s")
        print(f"Elapsed this run: {format_seconds(elapsed)}")
        print(f"Average per school: {avg_per_school:.2f}s")
        print(f"Estimated time left: {format_seconds(eta)}")

    print("=" * 70)
    print("Finished this run.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
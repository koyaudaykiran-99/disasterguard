import os
import sys
import json
import logging
from datetime import datetime, timezone
import httpx
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("disasterguard.dataset")

# Coordinate config: Chennai Metropolitan Region (Pilot Center)
LATITUDE = 13.0827
LONGITUDE = 80.2707
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_CSV = os.path.join(BASE_DIR, "ml", "datasets", "historical_weather_chennai_2022_2024.csv")
METADATA_JSON = os.path.join(BASE_DIR, "ml", "datasets", "historical_metadata.json")

def fetch_historical_dataset():
    """
    Ingest authentic hourly meteorological reanalysis data from Open-Meteo Historical Archive
    (ECMWF ERA5 & ERA5-Land Reanalysis models).
    """
    logger.info(f"Connecting to Open-Meteo Historical Archive API for coords ({LATITUDE}, {LONGITUDE})...")
    logger.info(f"Target date range: {START_DATE} to {END_DATE} (3 full years)")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": round(LATITUDE, 4),
        "longitude": round(LONGITUDE, 4),
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,rain,surface_pressure,wind_speed_10m,weather_code",
        "timezone": "auto"
    }

    try:
        with httpx.Client(timeout=45.0) as client:
            response = client.get(url, params=params)
            if response.status_code != 200:
                raise RuntimeError(f"Open-Meteo API returned status {response.status_code}: {response.text}")
            data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch historical dataset: {e}")
        raise

    hourly = data.get("hourly", {})
    if not hourly or "time" not in hourly:
        raise ValueError("API response missing hourly time-series data.")

    df = pd.DataFrame({
        "timestamp": hourly["time"],
        "temperature_c": hourly["temperature_2m"],
        "humidity_pct": hourly["relative_humidity_2m"],
        "precipitation_mm": hourly["precipitation"],
        "rain_mm": hourly["rain"],
        "surface_pressure_hpa": hourly["surface_pressure"],
        "wind_speed_kmh": hourly["wind_speed_10m"],
        "weather_code": hourly["weather_code"],
    })

    # Add spatial coordinates and provenance tracking
    df["latitude"] = LATITUDE
    df["longitude"] = LONGITUDE
    df["data_source"] = "ECMWF_ERA5_Land_OpenMeteo"
    df["dataset_type"] = "historical_real"

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logger.info(f"Successfully saved {len(df)} authentic historical records to: {OUTPUT_CSV}")

    # Write provenance metadata
    metadata = {
        "dataset_name": "Chennai Regional Historical Meteorological Dataset",
        "source": "Open-Meteo Historical Weather Archive API",
        "scientific_model": "ECMWF ERA5 / ERA5-Land Reanalysis",
        "source_url": "https://archive-api.open-meteo.com/v1/archive",
        "download_date": datetime.now(timezone.utc).isoformat(),
        "geographic_coverage": {
            "region": "Chennai Metropolitan Area, Tamil Nadu, India",
            "latitude": LATITUDE,
            "longitude": LONGITUDE
        },
        "temporal_coverage": {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "granularity": "1-hour"
        },
        "total_records": len(df),
        "columns": list(df.columns),
        "units": {
            "temperature_c": "degrees Celsius",
            "humidity_pct": "percent (0-100)",
            "precipitation_mm": "millimeters",
            "rain_mm": "millimeters",
            "surface_pressure_hpa": "hectopascals",
            "wind_speed_kmh": "kilometers per hour",
            "weather_code": "WMO standard synoptic weather code"
        },
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0) via Open-Meteo & ECMWF Copernicus",
        "dataset_type": "historical_real",
        "dataset_version": "v1.0-real-2022-2024"
    }

    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved dataset provenance metadata to: {METADATA_JSON}")

    return df

if __name__ == "__main__":
    fetch_historical_dataset()

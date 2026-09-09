import os
import sys
import json
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("disasterguard.quality")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "ml", "datasets", "historical_weather_chennai_2022_2024.csv")
REPORT_PATH = os.path.join(BASE_DIR, "ml", "datasets", "data_quality_report.json")

def run_quality_pipeline(csv_path: str = DATASET_PATH) -> dict:
    """
    Execute data quality validation pipeline on raw historical meteorological dataset.
    Validates monotonicity, null counts, duplicate records, physical ranges, and extreme events.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    logger.info(f"Initiating Data Quality Pipeline on: {csv_path}")
    df = pd.read_csv(csv_path)
    initial_count = len(df)
    logger.info(f"Loaded {initial_count} raw records.")

    # 1. Timestamp Monotonicity & Continuity
    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("dt").reset_index(drop=True)
    time_diffs = df["dt"].diff().dropna()
    expected_step = pd.Timedelta(hours=1)
    non_uniform_steps = int((time_diffs != expected_step).sum())
    is_monotonic = bool(df["dt"].is_monotonic_increasing)

    # 2. Duplicate Detection
    duplicate_timestamps = int(df["dt"].duplicated().sum())
    exact_duplicates = int(df.duplicated(subset=["timestamp", "temperature_c", "precipitation_mm"]).sum())

    # 3. Missing Value Analysis
    missing_counts = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())

    # 4. Domain Boundary Validation
    invalid_temp = int(((df["temperature_c"] < -10.0) | (df["temperature_c"] > 60.0)).sum())
    invalid_humidity = int(((df["humidity_pct"] < 0.0) | (df["humidity_pct"] > 100.0)).sum())
    invalid_pressure = int(((df["surface_pressure_hpa"] < 850.0) | (df["surface_pressure_hpa"] > 1080.0)).sum())
    invalid_precip = int((df["precipitation_mm"] < 0.0).sum())
    invalid_wind = int((df["wind_speed_kmh"] < 0.0).sum())

    domain_violations = invalid_temp + invalid_humidity + invalid_pressure + invalid_precip + invalid_wind

    # 5. Extreme Rainfall Event Statistics (Domain-Aware: MUST NOT BE DROPPED)
    heavy_rain_events = int((df["precipitation_mm"] >= 10.0).sum())
    very_heavy_rain_events = int((df["precipitation_mm"] >= 25.0).sum())
    extreme_convective_events = int((df["precipitation_mm"] >= 50.0).sum())
    max_1h_rainfall = float(df["precipitation_mm"].max())
    total_precip_mm = float(df["precipitation_mm"].sum())

    # 6. Overall Quality Assessment
    quality_status = "EXCELLENT" if (total_missing == 0 and domain_violations == 0 and is_monotonic) else "WARNING"

    report = {
        "dataset_file": os.path.basename(csv_path),
        "total_records": initial_count,
        "valid_records": initial_count - domain_violations,
        "removed_records": 0,  # Zero data lost; extreme events preserved
        "timestamp_checks": {
            "is_monotonic": is_monotonic,
            "duplicate_timestamps": duplicate_timestamps,
            "non_uniform_hour_steps": non_uniform_steps
        },
        "missing_values": {
            "total_missing_cells": total_missing,
            "by_column": {k: int(v) for k, v in missing_counts.items() if k != "dt"}
        },
        "domain_boundary_checks": {
            "invalid_temperatures": invalid_temp,
            "invalid_humidity": invalid_humidity,
            "invalid_pressure": invalid_pressure,
            "invalid_negative_rainfall": invalid_precip,
            "invalid_wind_speeds": invalid_wind,
            "total_violations": domain_violations
        },
        "meteorological_statistics": {
            "temperature_c": {
                "min": round(float(df["temperature_c"].min()), 1),
                "mean": round(float(df["temperature_c"].mean()), 1),
                "max": round(float(df["temperature_c"].max()), 1)
            },
            "relative_humidity_pct": {
                "min": round(float(df["humidity_pct"].min()), 1),
                "mean": round(float(df["humidity_pct"].mean()), 1),
                "max": round(float(df["humidity_pct"].max()), 1)
            },
            "surface_pressure_hpa": {
                "min": round(float(df["surface_pressure_hpa"].min()), 1),
                "mean": round(float(df["surface_pressure_hpa"].mean()), 1),
                "max": round(float(df["surface_pressure_hpa"].max()), 1)
            },
            "rainfall_distribution": {
                "total_cumulative_3y_mm": round(total_precip_mm, 1),
                "max_hourly_intensity_mm": round(max_1h_rainfall, 1),
                "moderate_heavy_hours_ge_10mm": heavy_rain_events,
                "heavy_rain_hours_ge_25mm": very_heavy_rain_events,
                "extreme_convective_hours_ge_50mm": extreme_convective_events
            }
        },
        "quality_status": quality_status,
        "timestamp_range": {
            "start": df["timestamp"].iloc[0],
            "end": df["timestamp"].iloc[-1]
        }
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Data Quality Pipeline finished with status: {quality_status}")
    logger.info(f"Quality Report generated at: {REPORT_PATH}")
    logger.info(f"Total Records: {initial_count} | Missing: {total_missing} | Max 1h Rain: {max_1h_rainfall} mm")
    logger.info(f"Heavy Rain Hours (>=10mm): {heavy_rain_events} | Extreme Rain Hours (>=50mm): {extreme_convective_events}")

    return report

if __name__ == "__main__":
    run_quality_pipeline()

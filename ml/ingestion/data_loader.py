import os
import json
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("disasterguard.ingestion")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RAW_CSV = os.path.join(BASE_DIR, "datasets", "historical_weather_chennai_2022_2024.csv")
DEFAULT_QUALITY_REPORT = os.path.join(BASE_DIR, "evaluation", "data_quality_report.json")

class HistoricalDataLoader:
    """
    Reusable data loader for real historical meteorological datasets.
    Handles file loading, ISO-8601 timestamp parsing, and strict column typing.
    """
    EXPECTED_COLUMNS = [
        "timestamp",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "rain_mm",
        "surface_pressure_hpa",
        "wind_speed_kmh",
        "weather_code"
    ]

    def __init__(self, filepath: str = DEFAULT_RAW_CSV):
        self.filepath = filepath

    def load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Historical dataset not found at: {self.filepath}")

        logger.info(f"Loading historical meteorological dataset from: {self.filepath}")
        df = pd.read_csv(self.filepath)

        missing_cols = set(self.EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset missing required columns: {missing_cols}")

        df["dt"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("dt").reset_index(drop=True)
        logger.info(f"Loaded {len(df)} historical observations from {df['dt'].min()} to {df['dt'].max()}")
        return df

class DataValidator:
    """
    Scientific validation pipeline for historical weather data.
    Validates monotonicity, null counts, duplicate records, physical ranges,
    and extreme event integrity without naive deletion.
    """
    def __init__(self, output_report_path: str = DEFAULT_QUALITY_REPORT):
        self.output_report_path = output_report_path

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        initial_count = len(df)
        col_count = len(df.columns)

        # 1. Monotonicity & Step Continuity
        dt_series = df["dt"] if "dt" in df.columns else pd.to_datetime(df["timestamp"], utc=True)
        is_monotonic = bool(dt_series.is_monotonic_increasing)
        time_diffs = dt_series.diff().dropna()
        expected_step = pd.Timedelta(hours=1)
        non_uniform_steps = int((time_diffs != expected_step).sum())

        # 2. Duplicate Detection
        duplicate_timestamps = int(dt_series.duplicated().sum())
        exact_duplicates = int(df.duplicated(subset=["timestamp", "temperature_c", "precipitation_mm"]).sum())

        # 3. Missing Value Analysis
        missing_counts = {col: int(df[col].isnull().sum()) for col in df.columns if col != "dt"}
        total_missing = sum(missing_counts.values())
        missing_pct = round((total_missing / (initial_count * max(col_count - 1, 1))) * 100, 4)

        # 4. Domain Boundary Checks
        invalid_temp = int(((df["temperature_c"] < -10.0) | (df["temperature_c"] > 60.0)).sum())
        invalid_humidity = int(((df["humidity_pct"] < 0.0) | (df["humidity_pct"] > 100.0)).sum())
        invalid_pressure = int(((df["surface_pressure_hpa"] < 850.0) | (df["surface_pressure_hpa"] > 1080.0)).sum())
        invalid_precip = int((df["precipitation_mm"] < 0.0).sum())
        invalid_wind = int((df["wind_speed_kmh"] < 0.0).sum())
        total_violations = invalid_temp + invalid_humidity + invalid_pressure + invalid_precip + invalid_wind

        # 5. Extreme Rainfall Statistics
        heavy_rain_events = int((df["precipitation_mm"] >= 10.0).sum())
        extreme_convective_events = int((df["precipitation_mm"] >= 50.0).sum())
        max_1h_rainfall = float(df["precipitation_mm"].max())
        total_precip_mm = float(df["precipitation_mm"].sum())

        report = {
            "row_count": initial_count,
            "column_count": col_count,
            "missing_values": {
                "total_missing_cells": total_missing,
                "missing_percentage": missing_pct,
                "by_column": missing_counts
            },
            "duplicates": {
                "duplicate_timestamps": duplicate_timestamps,
                "exact_duplicates": exact_duplicates
            },
            "invalid_values": {
                "invalid_temperatures": invalid_temp,
                "invalid_humidity": invalid_humidity,
                "invalid_pressure": invalid_pressure,
                "invalid_negative_rainfall": invalid_precip,
                "invalid_wind_speeds": invalid_wind,
                "total_violations": total_violations
            },
            "timestamp_checks": {
                "is_monotonic": is_monotonic,
                "non_uniform_hour_steps": non_uniform_steps
            },
            "date_range": {
                "start": str(dt_series.min()),
                "end": str(dt_series.max())
            },
            "geographic_range": {
                "region": "Chennai Metropolitan Area, Tamil Nadu, India",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "elevation_m": 12.0
            },
            "meteorological_statistics": {
                "temperature_c": {
                    "min": round(float(df["temperature_c"].min()), 1),
                    "mean": round(float(df["temperature_c"].mean()), 1),
                    "max": round(float(df["temperature_c"].max()), 1)
                },
                "surface_pressure_hpa": {
                    "min": round(float(df["surface_pressure_hpa"].min()), 1),
                    "mean": round(float(df["surface_pressure_hpa"].mean()), 1),
                    "max": round(float(df["surface_pressure_hpa"].max()), 1)
                },
                "relative_humidity_pct": {
                    "min": round(float(df["humidity_pct"].min()), 1),
                    "mean": round(float(df["humidity_pct"].mean()), 1),
                    "max": round(float(df["humidity_pct"].max()), 1)
                },
                "total_accumulated_precip_mm": round(total_precip_mm, 1),
                "max_hourly_precipitation_mm": round(max_1h_rainfall, 1),
                "heavy_rainfall_hours_gte_10mm": heavy_rain_events,
                "extreme_convective_hours_gte_50mm": extreme_convective_events
            },
            "validation_status": "PASSED" if (total_missing == 0 and total_violations == 0 and is_monotonic) else "WARNING"
        }

        os.makedirs(os.path.dirname(self.output_report_path), exist_ok=True)
        with open(self.output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Data quality report saved to: {self.output_report_path} (Status: {report['validation_status']})")
        return report

if __name__ == "__main__":
    loader = HistoricalDataLoader()
    df = loader.load_data()
    validator = DataValidator()
    report = validator.validate(df)
    print(f"Data Validation Complete: Status={report['validation_status']}, Rows={report['row_count']}")

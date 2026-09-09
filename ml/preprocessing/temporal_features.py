import os
import sys
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("disasterguard.features")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_CSV = os.path.join(BASE_DIR, "ml", "datasets", "historical_weather_chennai_2022_2024.csv")
ENGINEERED_CSV = os.path.join(BASE_DIR, "ml", "datasets", "engineered_historical_features.csv")

# Standardized feature column names expected by DisasterGuard ML models
FEATURE_COLUMNS = [
    "rainfall_1h",
    "rainfall_3h",
    "rainfall_6h",
    "rainfall_12h",
    "rainfall_24h",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
    "pressure_change_3h",
    "humidity_trend_3h"
]

def engineer_temporal_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct temporal rolling and trend features from chronological meteorological time series.
    Constructs forward-looking 6-hour targets without future data leakage into features.
    """
    logger.info("Starting temporal feature engineering...")
    df = raw_df.sort_values("timestamp").reset_index(drop=True).copy()
    p = df["precipitation_mm"]

    # --- Preceding Historical Features (Looking strictly backward from time t) ---
    # Shift by 1 ensures features at step t only use information strictly up to t-1
    df["rainfall_1h"] = p.shift(1).fillna(0.0)
    df["rainfall_3h"] = p.shift(1).rolling(window=3, min_periods=1).sum().fillna(0.0)
    df["rainfall_6h"] = p.shift(1).rolling(window=6, min_periods=1).sum().fillna(0.0)
    df["rainfall_12h"] = p.shift(1).rolling(window=12, min_periods=1).sum().fillna(0.0)
    df["rainfall_24h"] = p.shift(1).rolling(window=24, min_periods=1).sum().fillna(0.0)

    # Meteorological conditions at observation time
    df["temperature"] = df["temperature_c"]
    df["humidity"] = df["humidity_pct"]
    df["pressure"] = df["surface_pressure_hpa"]
    df["wind_speed"] = df["wind_speed_kmh"]

    # Derived atmospheric trend dynamics
    # Rapid pressure drop is a primary physical indicator of storm/cyclonic convection
    df["pressure_change_3h"] = (df["pressure"] - df["pressure"].shift(3)).fillna(0.0)
    df["humidity_trend_3h"] = (df["humidity"] - df["humidity"].shift(3)).fillna(0.0)

    # --- Forward-Looking Target Variables (Predicting t to t+6 hours) ---
    # Calculate cumulative sum of the upcoming 6 hours: [t, t+1, t+2, t+3, t+4, t+5]
    fwd_6h = p.iloc[::-1].rolling(window=6, min_periods=6).sum().iloc[::-1]
    df["predicted_rainfall_6h_mm"] = fwd_6h.round(2)

    # Multi-class target: Heavy rainfall tier
    def classify_rainfall(val):
        if pd.isna(val):
            return np.nan
        if val >= 50.0:
            return "EXTREME"
        elif val >= 20.0:
            return "HIGH"
        elif val >= 5.0:
            return "MODERATE"
        else:
            return "LOW"

    df["rainfall_category"] = df["predicted_rainfall_6h_mm"].apply(classify_rainfall)

    # Drop edge rows (initial 24 hours lacking full historical lag, and last 6 hours lacking target)
    clean_df = df.iloc[24:-6].reset_index(drop=True).copy()
    logger.info(f"Engineered {len(clean_df)} complete feature vectors.")

    return clean_df

def chronological_split(
    df: pd.DataFrame,
    train_pct: float = 0.70,
    val_pct: float = 0.15,
    test_pct: float = 0.15
):
    """
    Perform strict chronological time-series train/val/test split.
    Prevents future-information leakage into historical training representations.
    """
    assert abs((train_pct + val_pct + test_pct) - 1.0) < 1e-5, "Percentages must sum to 1.0"
    n = len(df)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    logger.info("Chronological Split Completed:")
    logger.info(f"  Training Set   ({train_pct*100:.0f}%): {len(train_df)} records [{train_df['timestamp'].iloc[0]} -> {train_df['timestamp'].iloc[-1]}]")
    logger.info(f"  Validation Set ({val_pct*100:.0f}%): {len(val_df)} records [{val_df['timestamp'].iloc[0]} -> {val_df['timestamp'].iloc[-1]}]")
    logger.info(f"  Test Set       ({test_pct*100:.0f}%): {len(test_df)} records [{test_df['timestamp'].iloc[0]} -> {test_df['timestamp'].iloc[-1]}]")

    return train_df, val_df, test_df

def generate_and_save_engineered_dataset():
    if not os.path.exists(RAW_CSV):
        raise FileNotFoundError(f"Raw dataset not found at {RAW_CSV}")
    
    raw_df = pd.read_csv(RAW_CSV)
    df = engineer_temporal_features(raw_df)
    df.to_csv(ENGINEERED_CSV, index=False)
    logger.info(f"Saved engineered dataset to: {ENGINEERED_CSV}")
    
    # Verify chronological split
    train_df, val_df, test_df = chronological_split(df)
    return df, train_df, val_df, test_df

if __name__ == "__main__":
    generate_and_save_engineered_dataset()

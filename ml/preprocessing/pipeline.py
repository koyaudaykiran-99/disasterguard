import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

RAINFALL_FEATURES = [
    "rainfall_1h",
    "rainfall_3h",
    "rainfall_6h",
    "rainfall_12h",
    "rainfall_24h",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed"
]

FLOOD_FEATURES = [
    "rainfall_intensity_mm_h",
    "cumulative_rainfall_24h",
    "elevation_m",
    "slope_deg",
    "drainage_proximity_m",
    "soil_saturation_pct"
]

class PreprocessingPipeline:
    """
    Standardized, reusable preprocessing pipeline for DisasterGuard ML models.
    Handles missing values, duplicate removal, feature subsetting, and scaling.
    """
    def __init__(self, feature_names, name="default"):
        self.feature_names = feature_names
        self.name = name
        self.pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        self.is_fitted = False

    def clean_raw_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates and reset index."""
        cleaned = df.drop_duplicates().copy()
        return cleaned

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract required feature subset, handling field aliases if needed."""
        data = df.copy()
        # Support aliases between API schema names and dataset column names
        if "rainfall_intensity_mm_h" in self.feature_names and "rainfall_intensity_mm_h" not in data.columns:
            if "rainfall_1h" in data.columns:
                data["rainfall_intensity_mm_h"] = data["rainfall_1h"]
        if "cumulative_rainfall_24h" in self.feature_names and "cumulative_rainfall_24h" not in data.columns:
            if "rainfall_24h" in data.columns:
                data["cumulative_rainfall_24h"] = data["rainfall_24h"]
        if "soil_saturation_pct" in self.feature_names and "soil_saturation_pct" not in data.columns:
            data["soil_saturation_pct"] = 65.0  # nominal median fallback

        missing_cols = [c for c in self.feature_names if c not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required features for {self.name}: {missing_cols}")
        
        return data[self.feature_names].astype(float)

    def fit(self, X: pd.DataFrame):
        X_sub = self.extract_features(X)
        self.pipeline.fit(X_sub)
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError(f"Pipeline {self.name} must be fitted before transforming.")
        X_sub = self.extract_features(X)
        return self.pipeline.transform(X_sub)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.fit(X).transform(X)

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"Saved preprocessing pipeline to: {filepath}")

    @staticmethod
    def load(filepath: str) -> "PreprocessingPipeline":
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preprocessor artifact not found at: {filepath}")
        return joblib.load(filepath)

def split_dataset(X: pd.DataFrame, y, test_size=0.2, random_state=42, stratify=None):
    """Perform train/test split with reproducible random seed."""
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify
    )

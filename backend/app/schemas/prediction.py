from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class RainfallPredictionRequest(BaseModel):
    location: str
    historical_rainfall_24h: float = 120.0
    humidity: float = 88.0
    temperature: float = 24.0
    pressure: float = 996.0
    wind_speed: float = 35.0
    forecast_horizon_hours: int = 6
    rainfall_1h: Optional[float] = None
    rainfall_3h: Optional[float] = None
    rainfall_6h: Optional[float] = None
    rainfall_12h: Optional[float] = None
    pressure_change_3h: Optional[float] = None
    humidity_trend_3h: Optional[float] = None

class RainfallPredictionResponse(BaseModel):
    predicted_rainfall_mm: float
    forecast_horizon_hours: int
    confidence: float
    risk_level: str
    predicted_category: Optional[str] = None
    model_name: Optional[str] = "RandomForestClassifier + Regressor (scikit-learn)"
    model_version: Optional[str] = "v2.0-real-data"
    training_dataset: Optional[str] = None
    data_source: Optional[str] = "ECMWF ERA5-Land Historical Reanalysis"
    data_source_type: Optional[str] = "historical_real"
    model_mode: str = "trained_ml_prototype"
    prediction_time: datetime = datetime.now()
    class_probabilities: Optional[dict] = None
    feature_importance: Optional[dict] = None
    top_contributors: Optional[list] = None
    weather_source: Optional[str] = None
    disclaimer: Optional[str] = None

class FloodPredictionRequest(BaseModel):
    location: str
    rainfall_intensity_mm_h: float = 45.0
    cumulative_rainfall_24h: float = 180.0
    elevation_m: float = 12.0
    slope_deg: float = 2.5
    drainage_proximity_m: float = 150.0
    soil_saturation_pct: Optional[float] = 75.0

class FloodPredictionResponse(BaseModel):
    flood_probability: float
    estimated_water_depth_m: float
    risk_level: str
    confidence: float
    model_name: Optional[str] = "RandomForestClassifier + Depth Regressor (scikit-learn)"
    model_version: Optional[str] = "v1.0-prototype"
    training_dataset: Optional[str] = "disaster_training_data.csv"
    data_source: Optional[str] = "Physically-Modeled Synthetic Hydrological Prototype"
    data_source_type: Optional[str] = "synthetic_prototype"
    model_mode: str = "trained_ml_prototype"
    prediction_time: datetime = datetime.now()
    class_probabilities: Optional[dict] = None
    feature_importance: Optional[dict] = None
    weather_source: Optional[str] = None
    risk_breakdown: Optional[dict] = None
    alert_recommendation: Optional[str] = None
    top_drivers: Optional[list] = None
    disclaimer: Optional[str] = None

class ModelMetricsResponse(BaseModel):
    training_timestamp: str
    dataset_samples: int
    data_provenance: str
    models: dict
    active_models: Optional[dict] = None
    registry_version: Optional[str] = None


from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.prediction import (
    RainfallPredictionRequest, RainfallPredictionResponse,
    FloodPredictionRequest, FloodPredictionResponse,
    ModelMetricsResponse
)
from app.services.prediction_service import prediction_service
from app.ml.prediction_service import ml_service

router = APIRouter()

# ---------------------------------------------------------------------------
# ML MODEL REGISTRY, PROVENANCE & EXPLANATION ENDPOINTS (Phase 5.1)
# ---------------------------------------------------------------------------

@router.get("/models")
def get_ml_models():
    """Retrieve full catalog of trained models from Model Manifest."""
    return ml_service.get_models()

@router.get("/models/active")
def get_active_ml_models():
    """Retrieve active production models, algorithms, and training datasets."""
    return ml_service.get_active_models()

@router.get("/models/metrics", response_model=ModelMetricsResponse)
@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """Retrieve genuine scikit-learn evaluation metrics, confusion matrix, and training provenance."""
    return ml_service.get_metrics()

@router.get("/models/{model_id}")
def get_ml_model_by_id(model_id: str):
    """Retrieve metadata and metrics for a specific model ID."""
    models_data = ml_service.get_models()
    for m in models_data.get("models", []):
        if m.get("model_id") == model_id:
            return m
    raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry")

@router.get("/provenance")
def get_ml_provenance():
    """Retrieve data source lineage, licenses, geographical scopes, and model assignments."""
    return ml_service.get_provenance()

@router.get("/explanation")
def get_ml_explanation(db: Session = Depends(get_db)):
    """Retrieve structured explanation separating facts, predictions, interpretations, and advisories."""
    from app.database.models.weather import WeatherObservation
    latest_weather = db.query(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).first()
    facts = None
    if latest_weather:
        facts = {
            "source": f"Open-Meteo ({latest_weather.source})",
            "location": latest_weather.location or "Chennai Metropolitan Area",
            "temperature_c": latest_weather.temperature,
            "humidity_pct": latest_weather.humidity,
            "surface_pressure_hpa": latest_weather.pressure,
            "wind_speed_kmh": latest_weather.wind_speed,
            "observed_at": latest_weather.observed_at.isoformat() if latest_weather.observed_at else None
        }
    return ml_service.get_explanation(observed_facts=facts)

# ---------------------------------------------------------------------------
# INFERENCE ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/rainfall", response_model=RainfallPredictionResponse)
def predict_rainfall(req: RainfallPredictionRequest, db: Session = Depends(get_db)):
    """AI Rainfall Prediction model endpoint."""
    return prediction_service.predict_rainfall(db, req.model_dump())

@router.get("/rainfall/latest", response_model=RainfallPredictionResponse)
def get_latest_rainfall_prediction(db: Session = Depends(get_db)):
    """Get latest AI rainfall prediction."""
    req = RainfallPredictionRequest(location="Central Metro Basin")
    return prediction_service.predict_rainfall(db, req.model_dump())

@router.post("/flood", response_model=FloodPredictionResponse)
def predict_flood(req: FloodPredictionRequest, db: Session = Depends(get_db)):
    """AI Flood Inundation Probability model endpoint."""
    return prediction_service.predict_flood(db, req.model_dump())

@router.get("/flood/latest", response_model=FloodPredictionResponse)
def get_latest_flood_prediction(db: Session = Depends(get_db)):
    """Get latest AI flood prediction."""
    req = FloodPredictionRequest(location="Central Metro Basin")
    return prediction_service.predict_flood(db, req.model_dump())

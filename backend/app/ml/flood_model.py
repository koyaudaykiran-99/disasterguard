from typing import Dict, Any
from app.ml.model_registry import BaseDisasterModel
from app.ml.prediction_service import ml_service

class FloodPredictor(BaseDisasterModel):
    def __init__(self):
        self.is_loaded = ml_service.is_loaded

    def load_model(self) -> bool:
        return ml_service.load_models()

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        return ml_service.predict_flood(features)

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ready" if ml_service.is_loaded else "uninitialized",
            "mode": "trained_ml_prototype",
            "version": "v1.0-scikit-learn"
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_type": "RandomForestClassifier + Depth Regressor (scikit-learn)",
            "features_used": [
                "rainfall_intensity_mm_h", "cumulative_rainfall_24h", "elevation_m",
                "slope_deg", "drainage_proximity_m", "soil_saturation_pct"
            ],
            "targets": ["flood_probability", "estimated_water_depth_m", "flood_risk_level"],
            "data_source": "Physically-Modeled Synthetic Hydrological Prototype"
        }

flood_predictor = FloodPredictor()

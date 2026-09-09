from typing import Dict, Any
from app.ml.model_registry import BaseDisasterModel
from app.ml.prediction_service import ml_service

class RainfallPredictor(BaseDisasterModel):
    def __init__(self):
        self.is_loaded = ml_service.is_loaded

    def load_model(self) -> bool:
        return ml_service.load_models()

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        return ml_service.predict_rainfall(features)

    def health_check(self) -> Dict[str, Any]:
        clf_meta = ml_service.active_meta.get("rainfall_classifier", {})
        return {
            "status": "ready" if ml_service.is_loaded else "uninitialized",
            "mode": "trained_ml_production" if "real-data" in clf_meta.get("version", "") else "trained_ml_prototype",
            "version": clf_meta.get("version", "v2.0-real-data"),
            "data_source_type": clf_meta.get("data_source_type", "historical_real")
        }

    def metadata(self) -> Dict[str, Any]:
        clf_meta = ml_service.active_meta.get("rainfall_classifier", {})
        return {
            "model_type": f"{clf_meta.get('algorithm', 'RandomForestClassifier')} + GradientBoostingRegressor (scikit-learn)",
            "version": clf_meta.get("version", "v2.0-real-data"),
            "features_used": clf_meta.get("features", [
                "rainfall_1h", "rainfall_3h", "rainfall_6h", "rainfall_12h", "rainfall_24h",
                "temperature", "humidity", "pressure", "wind_speed", "pressure_change_3h", "humidity_trend_3h"
            ]),
            "targets": ["predicted_rainfall_mm", "rainfall_category"],
            "data_source": "ECMWF ERA5-Land Historical Reanalysis (2022-2024)",
            "data_source_type": "historical_real"
        }

rainfall_predictor = RainfallPredictor()


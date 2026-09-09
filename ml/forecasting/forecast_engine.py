"""
Unified Multi-Horizon Forecast Engine Facade.
Coordinates features, horizons, uncertainty, trajectory, and early-warning escalation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import sys
import os

from .forecast_features import extract_forecast_features
from .horizon_engine import HorizonEngine
from .trajectory import TrajectoryEngine
from .escalation import EscalationEngine
from ml.geospatial.susceptibility import calculate_flood_susceptibility

class ForecastEngine:
    """
    Master multi-horizon flood risk forecasting engine.
    Labeled as EXPLAINABLE_FORECAST_ENGINE with strict scientific honesty guarantees.
    """

    MODEL_VERSION = "forecast_v1"
    DATA_SOURCE_TYPE = "EXPLAINABLE_FORECAST_ENGINE"

    @classmethod
    def compute_forecast(
        cls,
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        weather_data: Optional[Dict[str, Any]] = None,
        forecast_series: Optional[List[Dict[str, Any]]] = None,
        db_events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute comprehensive multi-horizon forecasting pipeline.
        """
        now = datetime.now(timezone.utc)

        # 1. Feature extraction
        features = extract_forecast_features(
            latitude=latitude,
            longitude=longitude,
            weather_data=weather_data,
            forecast_series=forecast_series,
            db_events=db_events
        )

        # 2. Current risk evaluation
        obs_rain = features["observed_rainfall"]
        current_suscep = calculate_flood_susceptibility(
            rainfall_1h=obs_rain["1h"],
            rainfall_24h=obs_rain["24h"],
            predicted_rainfall_6h=obs_rain["6h"],
            latitude=latitude,
            longitude=longitude
        )
        current_risk_score = current_suscep["susceptibility_score"]
        current_risk_level = current_suscep["risk_level"]

        # 3. Multi-horizon projections (1H, 3H, 6H, 12H, 24H)
        horizons_data = HorizonEngine.generate_all_horizons(
            latitude=latitude,
            longitude=longitude,
            features=features,
            now_time=now
        )

        # 4. Trajectory classification
        horizon_scores = {h: data["risk_score"] for h, data in horizons_data.items()}
        trajectory_res = TrajectoryEngine.classify_trajectory(
            current_risk=current_risk_score,
            horizon_scores=horizon_scores
        )

        # 5. Early-Warning Escalation & Structured Evidence
        escalation_res = EscalationEngine.evaluate_escalation(
            current_risk=current_risk_score,
            horizons_data=horizons_data,
            trajectory_info=trajectory_res.to_dict(),
            spatial_features=features["spatial"],
            weather_features=features
        )

        # 6. Aggregate Uncertainty Overview
        confidences = [data["confidence"] for data in horizons_data.values()]
        avg_confidence = round(sum(confidences) / len(confidences), 2)
        uncertainties = [data["uncertainty"] for data in horizons_data.values()]
        avg_uncertainty = round(sum(uncertainties) / len(uncertainties), 2)

        return {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "current": {
                "risk_score": current_risk_score,
                "risk_level": current_risk_level,
                "rainfall_1h_mm": obs_rain["1h"],
                "rainfall_24h_mm": obs_rain["24h"],
                "elevation_m": features["spatial"]["elevation"],
                "nearest_drainage": features["spatial"]["nearest_drainage"],
                "timestamp": now.isoformat()
            },
            "horizons": horizons_data,
            "trajectory": trajectory_res.to_dict(),
            "early_warning": escalation_res.to_dict(),
            "uncertainty_overview": {
                "average_confidence": avg_confidence,
                "average_uncertainty": avg_uncertainty,
                "confidence_rating": "HIGH" if avg_confidence >= 0.70 else "MEDIUM" if avg_confidence >= 0.50 else "LOW",
                "horizon_decay_active": True,
                "scientific_note": "Confidence systematically decreases as prediction horizon extends."
            },
            "explainability": escalation_res.evidence_categories,
            "provenance": {
                "model_version": cls.MODEL_VERSION,
                "data_source_type": cls.DATA_SOURCE_TYPE,
                "data_source": "ERA5-Land Reanalysis (2022-2024) + Open-Meteo NWP + Chennai Topographic/Drainage Geodetic Anchors",
                "is_hydraulic_simulation": False,
                "depth_type": "PROXY_ESTIMATE",
                "compliance": "Phase 5.3 Scientific Honesty Protocol"
            },
            "generated_at": now.isoformat()
        }

def calculate_multi_horizon_forecast(
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    weather_data: Optional[Dict[str, Any]] = None,
    forecast_series: Optional[List[Dict[str, Any]]] = None,
    db_events: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Top-level convenience function."""
    return ForecastEngine.compute_forecast(
        latitude=latitude,
        longitude=longitude,
        weather_data=weather_data,
        forecast_series=forecast_series,
        db_events=db_events
    )

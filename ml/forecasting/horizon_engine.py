"""
Standardized Multi-Horizon Forecast Engine.
Generates structured predictions for 1H, 3H, 6H, 12H, 24H horizons.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum

from ml.geospatial.susceptibility import calculate_flood_susceptibility
from ml.geospatial.inundation import InundationEstimator
from .uncertainty import UncertaintyEngine, ForecastConfidence

class ForecastHorizon(str, Enum):
    H1 = "1H"
    H3 = "3H"
    H6 = "6H"
    H12 = "12H"
    H24 = "24H"

class HorizonEngine:
    """
    Computes individual and multi-horizon risk predictions with explicit PROXY_ESTIMATE depth.
    """

    HORIZONS = [ForecastHorizon.H1, ForecastHorizon.H3, ForecastHorizon.H6, ForecastHorizon.H12, ForecastHorizon.H24]
    HOURS_MAP = {"1H": 1, "3H": 3, "6H": 6, "12H": 12, "24H": 24}

    @classmethod
    def generate_horizon_prediction(
        cls,
        horizon: str,
        latitude: float,
        longitude: float,
        features: Dict[str, Any],
        now_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a single horizon prediction dictionary.
        """
        norm_h = horizon.upper().strip()
        hours = cls.HOURS_MAP.get(norm_h, 6)
        now = now_time or datetime.now(timezone.utc)
        forecast_ts = (now + timedelta(hours=hours)).isoformat()
        valid_until = (now + timedelta(hours=hours + 1)).isoformat()

        # Cumulative anticipated rainfall for this horizon
        h_rains = features.get("horizon_rainfall", {})
        predicted_rain_mm = float(h_rains.get(norm_h, 15.0))
        obs_24h = float(features.get("observed_rainfall", {}).get("24h", 45.0))
        obs_1h = float(features.get("observed_rainfall", {}).get("1h", 10.0))

        # Re-evaluate flood susceptibility under horizon rainfall load
        # Antecedent rainfall + horizon projection
        simulated_24h = min(400.0, obs_24h + (predicted_rain_mm * 0.75))
        suscep_res = calculate_flood_susceptibility(
            rainfall_1h=obs_1h,
            rainfall_24h=simulated_24h,
            predicted_rainfall_6h=predicted_rain_mm,
            latitude=latitude,
            longitude=longitude
        )

        risk_score = suscep_res["susceptibility_score"]
        risk_level = suscep_res["risk_level"]

        # Inundation proxy depth estimation
        estimator = InundationEstimator()
        inund_res = estimator.estimate_water_depth(
            latitude=latitude,
            longitude=longitude,
            susceptibility_score=risk_score,
            rainfall_mm=predicted_rain_mm
        )

        # Uncertainty & confidence decomposition
        has_series = features.get("forecast_series_available", True)
        unc_res = UncertaintyEngine.evaluate_horizon_uncertainty(
            horizon=norm_h,
            has_forecast_series=has_series
        )

        return {
            "horizon": norm_h,
            "forecast_timestamp": forecast_ts,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "rainfall_estimate_mm": predicted_rain_mm,
            "flood_susceptibility": risk_score,
            "proxy_depth_estimate_m": inund_res["estimated_depth_m"],
            "depth_type": "PROXY_ESTIMATE",
            "is_hydraulic_simulation": False,
            "confidence": unc_res.confidence,
            "uncertainty": unc_res.uncertainty,
            "confidence_level": unc_res.confidence_level.value,
            "uncertainty_summary": unc_res.factors_summary,
            "model_version": "forecast_v1",
            "data_source": "REAL_WEATHER + REAL_HISTORICAL_ML + GEOSPATIAL_DERIVATION",
            "generated_at": now.isoformat(),
            "valid_until": valid_until
        }

    @classmethod
    def generate_all_horizons(
        cls,
        latitude: float,
        longitude: float,
        features: Dict[str, Any],
        now_time: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate full dictionary of predictions across 1H, 3H, 6H, 12H, 24H.
        """
        now = now_time or datetime.now(timezone.utc)
        results = {}
        for h in ["1H", "3H", "6H", "12H", "24H"]:
            results[h] = cls.generate_horizon_prediction(
                horizon=h,
                latitude=latitude,
                longitude=longitude,
                features=features,
                now_time=now
            )
        return results

"""
Multi-Horizon Forecast Feature Extraction Engine.
Extracts multi-scale meteorological, topographic, hydrographic, and historical memory features.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import sys
import os

from ml.geospatial.spatial_features import extract_spatial_features

def extract_forecast_features(
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    weather_data: Optional[Dict[str, Any]] = None,
    forecast_series: Optional[List[Dict[str, Any]]] = None,
    db_events: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Extract unified feature dictionary for multi-horizon flood risk forecasting.
    """
    weather = weather_data or {}

    # Atmospheric & precipitation observations
    rain_1h = float(weather.get("rainfall_1h", 12.0) or 0.0)
    rain_3h = float(weather.get("rainfall_3h", rain_1h * 2.8) or 0.0)
    rain_6h = float(weather.get("rainfall_6h", rain_1h * 5.2) or 0.0)
    rain_12h = float(weather.get("rainfall_12h", rain_1h * 9.5) or 0.0)
    rain_24h = float(weather.get("rainfall_24h", rain_1h * 15.0) or 0.0)

    temperature = float(weather.get("temperature", 28.0) or 28.0)
    humidity = float(weather.get("humidity", 75.0) or 75.0)
    pressure = float(weather.get("pressure", 1008.0) or 1008.0)
    wind_speed = float(weather.get("wind_speed", 15.0) or 15.0)
    condition = str(weather.get("condition", "Rain") or "Rain")
    weather_source = str(weather.get("source", "real") or "real")

    # Dynamic atmospheric trends
    press_change = -2.5 if rain_1h > 15.0 else -1.0 if rain_1h > 5.0 else 0.0
    pressure_change_3h = float(weather.get("pressure_change_3h", press_change) or press_change)
    hum_trend = 5.0 if rain_1h > 10.0 else 1.5 if rain_1h > 2.0 else 0.0
    humidity_trend_3h = float(weather.get("humidity_trend_3h", hum_trend) or hum_trend)

    # Topographic, hydrographic, and historical memory
    spatial = extract_spatial_features(latitude, longitude, db_events=db_events)

    # Compute anticipated rainfall by horizon from forecast series (if available)
    horizon_rainfall = {}
    if forecast_series and len(forecast_series) > 0:
        # Sum precipitation from hourly forecast series
        hourly_rains = [float(f.get("precipitation_mm", 0.0) or 0.0) for f in forecast_series]
        horizon_rainfall["1H"] = round(sum(hourly_rains[:1]) if len(hourly_rains) >= 1 else rain_1h, 2)
        horizon_rainfall["3H"] = round(sum(hourly_rains[:3]) if len(hourly_rains) >= 3 else rain_1h * 2.5, 2)
        horizon_rainfall["6H"] = round(sum(hourly_rains[:6]) if len(hourly_rains) >= 6 else rain_1h * 4.5, 2)
        horizon_rainfall["12H"] = round(sum(hourly_rains[:12]) if len(hourly_rains) >= 12 else rain_1h * 7.5, 2)
        horizon_rainfall["24H"] = round(sum(hourly_rains[:24]) if len(hourly_rains) >= 24 else rain_1h * 12.0, 2)
    else:
        # Synthetic estimation from current intensity with decay/build-up curve
        # Cloudburst scenario: peak around 6h-12h
        multiplier = 1.0
        if rain_1h > 20.0:
            multiplier = 1.25  # severe monsoon intensification
        horizon_rainfall["1H"] = round(rain_1h * 1.05 * multiplier, 2)
        horizon_rainfall["3H"] = round(rain_1h * 2.8 * multiplier, 2)
        horizon_rainfall["6H"] = round(rain_1h * 5.2 * multiplier, 2)
        horizon_rainfall["12H"] = round(rain_1h * 8.5 * multiplier, 2)
        horizon_rainfall["24H"] = round(rain_1h * 13.0 * multiplier, 2)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "observed_rainfall": {
            "1h": rain_1h,
            "3h": rain_3h,
            "6h": rain_6h,
            "12h": rain_12h,
            "24h": rain_24h
        },
        "atmospheric": {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "condition": condition,
            "pressure_change_3h": pressure_change_3h,
            "humidity_trend_3h": humidity_trend_3h,
            "source": weather_source
        },
        "spatial": spatial,
        "horizon_rainfall": horizon_rainfall,
        "forecast_series_available": bool(forecast_series and len(forecast_series) > 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

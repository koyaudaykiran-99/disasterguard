"""
Forecasting Model Registry Metadata & Manifest Specifications.
"""

FORECAST_MODEL_METADATA = {
    "model_id": "forecast_v1",
    "model_name": "Multi-Horizon Flood Risk & Early Warning Engine",
    "type": "multi_horizon_risk_forecast",
    "version": "1.0",
    "status": "ACTIVE",
    "data_source": "real_historical + live_weather + geospatial",
    "data_source_type": "EXPLAINABLE_FORECAST_ENGINE",
    "horizons": ["1H", "3H", "6H", "12H", "24H"],
    "is_hydraulic_simulation": False,
    "depth_type": "PROXY_ESTIMATE",
    "inputs": [
        "temperature_c", "relative_humidity_pct", "precipitation_mm", "rain_mm",
        "surface_pressure_hpa", "wind_speed_kmh", "pressure_change_3h", "humidity_trend_3h",
        "elevation_m", "slope_deg", "drainage_distance_km", "drainage_bottleneck_factor",
        "historical_flood_proximity_score"
    ],
    "outputs": [
        "horizon", "risk_score", "risk_level", "rainfall_estimate_mm",
        "flood_susceptibility", "proxy_depth_estimate_m", "confidence",
        "uncertainty", "trajectory", "warning_state", "explanation"
    ],
    "limitations": [
        "Not a 2D hydrodynamic / shallow water simulation",
        "Proxy depth estimate only; does not claim centimeter-level physical precision",
        "Forecast uncertainty systematically increases with temporal horizon",
        "Atmospheric reanalysis and point sensors do not replace urban storm-water telemetry",
        "Decision support only; human operator confirmation remains strictly mandatory for rescue dispatch"
    ]
}

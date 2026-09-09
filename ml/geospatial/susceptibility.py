"""
Explainable Geospatial Flood Susceptibility Engine.
Combines multi-scale meteorological rainfall load, terrain topography, drainage proximity,
and historical memory into a normalized 0-100 flood susceptibility score.
"""

from typing import Dict, Any, List
from .spatial_features import extract_spatial_features
from .provider import DataSourceType

def calculate_flood_susceptibility(
    rainfall_1h: float = 15.0,
    rainfall_3h: float = None,
    rainfall_6h: float = None,
    rainfall_12h: float = None,
    rainfall_24h: float = None,
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    predicted_rainfall_6h: float = 0.0,
    db_events: list = None,
    rainfall_forecast_mm: float = None,
    antecedent_rainfall_mm: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate composite geospatial flood susceptibility score (0-100).
    Classifications:
      0-24: LOW
      25-49: MODERATE
      50-74: HIGH
      75-100: CRITICAL

    IMPORTANT: This is a susceptibility/risk intelligence score indicating relative
    vulnerability, NOT a physical hydrodynamic guarantee of flood occurrence.
    """
    # Normalize inputs
    if rainfall_forecast_mm is not None:
        predicted_rainfall_6h = rainfall_forecast_mm
        if rainfall_6h is None:
            rainfall_6h = rainfall_forecast_mm
    if antecedent_rainfall_mm is not None and rainfall_24h is None:
        rainfall_24h = antecedent_rainfall_mm

    rf_24h = rainfall_24h if rainfall_24h is not None else (rainfall_1h * 4.0)
    rf_6h = rainfall_6h if rainfall_6h is not None else (rainfall_1h * 2.5)

    spatial = extract_spatial_features(latitude, longitude, db_events=db_events)

    # 1. Rainfall Load Component (0-100) - 40% weight
    # 24h antecedent rainfall (heavy monsoon benchmark: 200mm = 100)
    rf_24h_norm = min(100.0, (rf_24h / 200.0) * 100.0)
    # 6h short-term intensity (critical cloudburst benchmark: 80mm = 100)
    rf_6h_effective = max(rf_6h, predicted_rainfall_6h)
    rf_6h_norm = min(100.0, (rf_6h_effective / 80.0) * 100.0)
    rainfall_component = round(0.55 * rf_24h_norm + 0.45 * rf_6h_norm, 1)

    # 2. Terrain Topographic Component (0-100) - 25% weight
    terrain_component = spatial["terrain_risk"]

    # 3. Drainage Proximity Component (0-100) - 20% weight
    drainage_component = spatial["drainage_risk"]

    # 4. Historical Disaster Memory Component (0-100) - 15% weight
    historical_component = spatial["historical_flood_score"]

    # Weighted Composite Score (0-100)
    composite_score = (
        0.40 * rainfall_component +
        0.25 * terrain_component +
        0.20 * drainage_component +
        0.15 * historical_component
    )
    score_int = int(round(max(0.0, min(100.0, composite_score))))

    # Risk level classification
    if score_int >= 75:
        risk_level = "CRITICAL"
        color_code = "rose"
    elif score_int >= 50:
        risk_level = "HIGH"
        color_code = "orange"
    elif score_int >= 25:
        risk_level = "MODERATE"
        color_code = "amber"
    else:
        risk_level = "LOW"
        color_code = "cyan"

    # Strict Categorical Explainability Breakdown (FACT, ML_PREDICTION, GEOSPATIAL_DERIVATION, AI_INTERPRETATION, RECOMMENDATION)
    explanation_categories = {
        "FACT": [
            f"Observed 24h cumulative rainfall is {rainfall_24h:.1f} mm (1h current: {rainfall_1h:.1f} mm).",
            f"Location coordinates [{latitude:.4f}, {longitude:.4f}] situated at elevation {spatial['elevation']} m ASL.",
            f"Distance to nearest primary drainage channel ({spatial['nearest_drainage']}) is {spatial['distance_to_drainage_km']} km."
        ],
        "ML_PREDICTION": [
            f"Real-historical rainfall model projects forward 6h accumulation of {predicted_rainfall_6h:.1f} mm.",
            f"Rainfall load normalized stress index: {rainfall_component}/100."
        ],
        "GEOSPATIAL_DERIVATION": [
            f"Topographic slope {spatial['slope']}° with relative elevation {spatial['relative_elevation']} m produces terrain susceptibility of {terrain_component}/100.",
            f"Hydraulic drainage bottleneck vulnerability calculated at {drainage_component}/100.",
            f"Historical disaster exposure index is {historical_component}/100 based on {spatial['historical_event_count']} recorded events."
        ],
        "AI_INTERPRETATION": [
            f"Combined hydrological stress ({rainfall_component}/100) and low-lying topography ({terrain_component}/100) indicate {risk_level} inundation susceptibility."
        ],
        "RECOMMENDATION": [
            "Command Centre operator review recommended for field staging." if score_int >= 50 else "Maintain routine telemetry monitoring.",
            "Alert field units to check storm-drain blockage near " + spatial['nearest_drainage'] if score_int >= 75 else "Follow standard meteorological monitoring protocols."
        ]
    }

    return {
        "susceptibility_score": score_int,
        "risk_level": risk_level,
        "color_code": color_code,
        "components": {
            "rainfall_component": rainfall_component,
            "terrain_component": terrain_component,
            "drainage_component": drainage_component,
            "historical_component": historical_component,
            "weights": {
                "rainfall": 0.40,
                "terrain": 0.25,
                "drainage": 0.20,
                "historical": 0.15
            }
        },
        "spatial_features": spatial,
        "explanation": explanation_categories,
        "model_version": "v2.1-geospatial",
        "data_source_type": DataSourceType.DERIVED.value,
        "limitations": [
            "Susceptibility score represents relative geographic hazard, not a 2D hydrodynamic simulation.",
            "Drainage model accounts for major waterways; micro-level stormwater street drains not modeled."
        ]
    }

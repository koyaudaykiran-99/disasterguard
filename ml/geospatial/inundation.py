"""
Flood Inundation Intelligence Estimator.
Generates proxy water-depth estimates and affected inundation extents with explicit scientific boundaries.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from .susceptibility import calculate_flood_susceptibility
from .provider import DataSourceType

class InundationEstimator:
    """
    Produces estimated inundation depths and polygon bounding extents.
    Strictly tags water depth as PROXY_ESTIMATE.
    """

    def estimate_water_depth(
        self,
        latitude: float,
        longitude: float,
        susceptibility_score: float = 50.0,
        rainfall_mm: float = 20.0
    ) -> Dict[str, Any]:
        """Calculates proxy water depth with explicit scientific boundary tags."""
        score = susceptibility_score
        if score < 25:
            depth = round(score * 0.006, 2)
            confidence = 0.85
        elif score < 50:
            depth = round(0.15 + (score - 25) * 0.012, 2)
            confidence = 0.78
        elif score < 75:
            depth = round(0.45 + (score - 50) * 0.02, 2)
            confidence = 0.72
        else:
            depth = round(0.95 + (score - 75) * 0.05, 2)
            confidence = 0.65
        return {
            "estimated_depth_m": depth,
            "depth_type": "PROXY_ESTIMATE",
            "is_hydraulic_simulation": False,
            "confidence": confidence,
            "susceptibility_score": score,
            "disclaimer": "Water depth is a proxy estimate; not a 2D hydraulic simulation."
        }

    def generate_inundation_polygon(
        self,
        latitude: float,
        longitude: float,
        susceptibility_score: float = 50.0
    ) -> Dict[str, Any]:
        """Generates GeoJSON polygon feature around coordinate."""
        delta = max(0.005, (susceptibility_score / 100.0) * 0.015)
        coords = [
            [round(longitude - delta, 5), round(latitude - delta, 5)],
            [round(longitude + delta, 5), round(latitude - delta, 5)],
            [round(longitude + delta, 5), round(latitude + delta, 5)],
            [round(longitude - delta, 5), round(latitude + delta, 5)],
            [round(longitude - delta, 5), round(latitude - delta, 5)],
        ]
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            },
            "properties": {
                "susceptibility_score": susceptibility_score,
                "depth_type": "PROXY_ESTIMATE"
            }
        }

    @staticmethod
    def estimate_inundation(
        rainfall_1h: float,
        rainfall_3h: float,
        rainfall_6h: float,
        rainfall_12h: float,
        rainfall_24h: float,
        latitude: float,
        longitude: float,
        predicted_rainfall_6h: float = 0.0,
        db_events: list = None
    ) -> Dict[str, Any]:
        """
        Estimate flood inundation risk, proxy depth, and affected area.
        """
        susc = calculate_flood_susceptibility(
            rainfall_1h=rainfall_1h,
            rainfall_3h=rainfall_3h,
            rainfall_6h=rainfall_6h,
            rainfall_12h=rainfall_12h,
            rainfall_24h=rainfall_24h,
            latitude=latitude,
            longitude=longitude,
            predicted_rainfall_6h=predicted_rainfall_6h,
            db_events=db_events
        )

        score = susc["susceptibility_score"]

        # Proxy water depth calculation:
        # Score < 25: 0.0 - 0.15m (puddle / minor curb water)
        # Score 25-49: 0.15 - 0.45m (ankle to calf depth)
        # Score 50-74: 0.45 - 0.95m (knee to waist depth)
        # Score 75-100: 0.95 - 2.20m (waist to chest depth / hazardous)
        if score < 25:
            estimated_depth = round(score * 0.006, 2)
            confidence = 0.85
            affected_km2 = round(0.1 + score * 0.02, 2)
        elif score < 50:
            estimated_depth = round(0.15 + (score - 25) * 0.012, 2)
            confidence = 0.78
            affected_km2 = round(0.6 + (score - 25) * 0.08, 2)
        elif score < 75:
            estimated_depth = round(0.45 + (score - 50) * 0.02, 2)
            confidence = 0.72
            affected_km2 = round(2.6 + (score - 50) * 0.20, 2)
        else:
            estimated_depth = round(0.95 + (score - 75) * 0.05, 2)
            confidence = 0.65
            affected_km2 = round(7.6 + (score - 75) * 0.40, 2)

        # Inundation footprint polygon around coordinate (+/- delta offset scaled by score)
        delta_lat = max(0.005, (score / 100.0) * 0.015)
        delta_lng = max(0.005, (score / 100.0) * 0.015)

        polygon = [
            [round(latitude - delta_lat, 5), round(longitude - delta_lng, 5)],
            [round(latitude - delta_lat, 5), round(longitude + delta_lng, 5)],
            [round(latitude + delta_lat, 5), round(longitude + delta_lng, 5)],
            [round(latitude + delta_lat, 5), round(longitude - delta_lng, 5)],
        ]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(latitude, 5),
            "longitude": round(longitude, 5),
            "risk_level": susc["risk_level"],
            "susceptibility_score": score,
            "estimated_depth_m": estimated_depth,
            "depth_confidence": confidence,
            "depth_type": "PROXY_ESTIMATE",  # NEVER claims OBSERVED without ground truth sensors
            "affected_area_km2": affected_km2,
            "polygon_coordinates": polygon,
            "components": susc["components"],
            "spatial_features": susc["spatial_features"],
            "explanation": susc["explanation"],
            "model_version": "v2.1-geospatial",
            "data_source_type": DataSourceType.DERIVED.value,
            "disclaimer": (
                "Water depth is a PROXY ESTIMATE derived from precipitation load, relative elevation, "
                "and hydrographic drainage proximity. Not a certified hydraulic or hydrodynamic simulation."
            )
        }

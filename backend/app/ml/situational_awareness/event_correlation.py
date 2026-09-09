"""
AI-DisasterGuard — Event Correlation Intelligence
Phase 6: Multi-Signal Spatio-Temporal Correlation Without SOS Merging
"""

import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from app.gis.spatial_queries import haversine_distance_km

logger = logging.getLogger("disasterguard.ml.situational_awareness.event_correlation")


class EventCorrelator:
    """
    Correlates multiple emergency signals across weather, spatial risk, and active incidents.
    CRITICAL INVARIANT: Never merges, alters, or destroys individual SOS/Incident identities.
    """

    def __init__(
        self,
        spatial_radius_km: float = 3.0,
        temporal_window_minutes: int = 45,
    ):
        self.spatial_radius_km = spatial_radius_km
        self.temporal_window_minutes = temporal_window_minutes

    def correlate_signals(
        self,
        incidents: List[Dict[str, Any]],
        weather_data: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        flood_susceptibility_zones: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Identify correlated incident groups and environmental compounding factors.
        Returns correlation records with confidence and explainable reasoning.
        """
        correlations: List[Dict[str, Any]] = []
        if len(incidents) < 2:
            return correlations

        # 1. Spatio-temporal incident clustering
        visited = set()
        for i, inc_a in enumerate(incidents):
            inc_a_id = inc_a.get("id")
            if inc_a_id in visited:
                continue

            lat_a = float(inc_a.get("latitude", 0.0))
            lng_a = float(inc_a.get("longitude", 0.0))
            created_a = self._parse_time(inc_a.get("created_at"))

            related = [inc_a_id]
            hazards = [inc_a.get("emergency_type") or inc_a.get("severity") or "FLOOD"]

            for j, inc_b in enumerate(incidents[i + 1:], start=i + 1):
                inc_b_id = inc_b.get("id")
                if inc_b_id in visited:
                    continue

                lat_b = float(inc_b.get("latitude", 0.0))
                lng_b = float(inc_b.get("longitude", 0.0))
                created_b = self._parse_time(inc_b.get("created_at"))

                dist = haversine_distance_km(lat_a, lng_a, lat_b, lng_b)
                time_diff = abs((created_a - created_b).total_seconds()) / 60.0

                if dist <= self.spatial_radius_km and time_diff <= self.temporal_window_minutes:
                    related.append(inc_b_id)
                    hazards.append(inc_b.get("emergency_type") or inc_b.get("severity") or "FLOOD")

            if len(related) >= 2:
                for r in related:
                    visited.add(r)

                correlation_id = f"CORR-{inc_a_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
                
                # Check compounding weather / flood factors
                rain_rate = 0.0
                if weather_data:
                    rain_rate = float(weather_data.get("rainfall_mm") or weather_data.get("precipitation_mm") or 0.0)

                compounding_factors: List[str] = []
                if rain_rate >= 25.0:
                    compounding_factors.append(f"Heavy precipitation ({rain_rate} mm/h)")

                if forecast_data:
                    trajectory = forecast_data.get("trajectory", "STABLE")
                    if trajectory in ["INCREASING", "RAPIDLY_INCREASING"]:
                        compounding_factors.append(f"Forecast risk trajectory is {trajectory}")

                reason_parts = [
                    f"{len(related)} active distress incidents reported within {self.spatial_radius_km}km in a {self.temporal_window_minutes}min window."
                ]
                if compounding_factors:
                    reason_parts.append(f"Compounded by {'; '.join(compounding_factors)}.")

                confidence = min(0.98, 0.70 + (len(related) * 0.05) + (0.10 if compounding_factors else 0.0))

                correlations.append({
                    "correlation_id": correlation_id,
                    "incident_ids": related,
                    "correlation_type": "SPATIAL_TEMPORAL_CONVERGENCE",
                    "confidence": round(confidence, 2),
                    "correlation_reason": " ".join(reason_parts),
                    "centroid": {
                        "latitude": round(lat_a, 4),
                        "longitude": round(lng_a, 4),
                    },
                    "dominant_hazard": hazards[0] if hazards else "FLOOD",
                })

        return correlations

    @staticmethod
    def _parse_time(time_val: Any) -> datetime:
        """Helper to safely parse timestamps."""
        if isinstance(time_val, datetime):
            return time_val if time_val.tzinfo else time_val.replace(tzinfo=timezone.utc)
        if isinstance(time_val, str):
            try:
                return datetime.fromisoformat(time_val.replace("Z", "+00:00"))
            except Exception:
                pass
        return datetime.now(timezone.utc)

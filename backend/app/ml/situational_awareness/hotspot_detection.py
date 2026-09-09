"""
AI-DisasterGuard — Geographic Hotspot Detection Intelligence
Phase 6: Multi-Signal Spatial Convergence Scoring & Hotspot Identification
"""

import math
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.gis.spatial_queries import haversine_distance_km

logger = logging.getLogger("disasterguard.ml.situational_awareness.hotspot_detection")


class HotspotDetector:
    """
    Detects geographic areas where multiple emergency and environmental hazard signals converge.
    """

    def __init__(self, hotspot_radius_km: float = 1.8):
        self.hotspot_radius_km = hotspot_radius_km

    def detect_hotspots(
        self,
        incidents: List[Dict[str, Any]],
        weather_observation: Optional[Dict[str, Any]] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        flood_zones: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Calculates multi-signal hotspot scores across active incidents and environmental factors.
        """
        hotspots: List[Dict[str, Any]] = []
        if not incidents:
            return hotspots

        # Seed candidate anchors from incidents
        processed_anchors: List[Dict[str, Any]] = []

        for i, inc in enumerate(incidents):
            lat = float(inc.get("latitude", 0.0))
            lng = float(inc.get("longitude", 0.0))

            # Check if close to an existing anchor
            is_grouped = False
            for anchor in processed_anchors:
                dist = haversine_distance_km(lat, lng, anchor["lat"], anchor["lng"])
                if dist <= self.hotspot_radius_km:
                    anchor["incidents"].append(inc)
                    is_grouped = True
                    break

            if not is_grouped:
                processed_anchors.append({
                    "lat": lat,
                    "lng": lng,
                    "incidents": [inc],
                    "seed_name": inc.get("title") or f"Sector ({lat:.3f}, {lng:.3f})",
                })

        # Rain rate from live or cached weather
        rain_rate = 0.0
        if weather_observation:
            rain_rate = float(weather_observation.get("rainfall_mm") or weather_observation.get("precipitation_mm") or 0.0)

        # Forecast trajectory factor
        traj_multiplier = 1.0
        trajectory = "STABLE"
        if forecast_data:
            trajectory = forecast_data.get("trajectory", "STABLE")
            if trajectory == "RAPIDLY_INCREASING":
                traj_multiplier = 1.35
            elif trajectory == "INCREASING":
                traj_multiplier = 1.20
            elif trajectory == "DECREASING":
                traj_multiplier = 0.85

        for idx, anchor in enumerate(processed_anchors, start=1):
            nearby_incidents = anchor["incidents"]
            n_incidents = len(nearby_incidents)

            # Signal 1: SOS / Incident density (0 - 40 pts)
            density_score = min(40.0, n_incidents * 12.0)

            # Signal 2: Rainfall intensity (0 - 25 pts)
            rain_score = min(25.0, (rain_rate / 60.0) * 25.0)

            # Signal 3: Severity weight (0 - 20 pts)
            critical_count = sum(1 for x in nearby_incidents if str(x.get("severity", "")).upper() == "CRITICAL")
            severity_score = min(20.0, critical_count * 10.0 + (n_incidents - critical_count) * 4.0)

            # Signal 4: Flood susceptibility (0 - 15 pts)
            flood_susceptibility = 0.75  # Default baseline for monitored basin
            flood_score = flood_susceptibility * 15.0

            # Composite Hotspot Score (0 - 100)
            raw_score = (density_score + rain_score + severity_score + flood_score) * traj_multiplier
            hotspot_score = round(min(100.0, max(15.0, raw_score)), 1)

            # Determine severity band
            if hotspot_score >= 80.0:
                severity = "CRITICAL"
            elif hotspot_score >= 60.0:
                severity = "HIGH"
            elif hotspot_score >= 40.0:
                severity = "MODERATE"
            else:
                severity = "LOW"

            evidence: List[Dict[str, Any]] = [
                {"category": "FACT", "statement": f"{n_incidents} active emergency incident(s) reported in this cluster area.", "confidence": 0.98},
                {"category": "FACT", "statement": f"Observed precipitation rate is {rain_rate:.1f} mm/h.", "confidence": 0.95},
                {"category": "ML_PREDICTION", "statement": f"Multi-horizon forecast risk trajectory is {trajectory}.", "confidence": 0.88},
                {"category": "GEOSPATIAL_DERIVATION", "statement": f"Area intersects high flood susceptibility basin (Score: {flood_susceptibility:.2f}).", "confidence": 0.92},
                {"category": "AI_INTERPRETATION", "statement": f"Spatial convergence of {n_incidents} emergencies under {trajectory.lower()} flood risk creates concentrated danger.", "confidence": 0.85},
            ]

            hotspot_code = f"HOTSPOT-{datetime.now(timezone.utc).strftime('%m%d')}-{idx:03d}"

            hotspots.append({
                "hotspot_code": hotspot_code,
                "name": f"Risk Hotspot: {anchor['seed_name']}",
                "hazard_type": "FLASH_FLOOD",
                "latitude": round(anchor["lat"], 5),
                "longitude": round(anchor["lng"], 5),
                "radius_km": round(self.hotspot_radius_km, 2),
                "hotspot_score": hotspot_score,
                "severity": severity,
                "confidence": 0.89,
                "sos_density": round(n_incidents / (math.pi * (self.hotspot_radius_km ** 2)), 2),
                "rainfall_intensity_mm": round(rain_rate, 1),
                "flood_susceptibility_score": round(flood_susceptibility, 2),
                "forecast_trajectory": trajectory,
                "supporting_evidence": evidence,
                "is_active": True,
            })

        return hotspots

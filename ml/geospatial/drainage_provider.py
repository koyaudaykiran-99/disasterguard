"""
Drainage and Hydrographic Network Intelligence Provider.
Computes distance and overflow susceptibility relative to primary natural and urban drainage channels.
"""

import math
from typing import Dict, Any, List
from .provider import BaseGeospatialProvider, DataSourceType, GeospatialProvenance

class DrainageProvider(BaseGeospatialProvider):
    """
    Evaluates proximity and hydraulic bottleneck risk relative to major Chennai drainage arteries.
    """

    MAJOR_DRAINAGE_CORRIDORS = [
        {
            "name": "Adyar River Basin",
            "type": "NATURAL_RIVER",
            "capacity_m3s": 1200,
            "segments": [
                (13.0100, 80.1700),
                (13.0120, 80.2000),
                (13.0150, 80.2300),
                (13.0130, 80.2600),
                (13.0080, 80.2750), # Adyar Estuary
            ]
        },
        {
            "name": "Cooum River Basin",
            "type": "NATURAL_RIVER",
            "capacity_m3s": 650,
            "segments": [
                (13.0720, 80.1600),
                (13.0750, 80.2100),
                (13.0780, 80.2500),
                (13.0690, 80.2850), # Cooum Mouth
            ]
        },
        {
            "name": "Buckingham Canal",
            "type": "CANAL_DRAIN",
            "capacity_m3s": 280,
            "segments": [
                (13.1300, 80.2800),
                (13.0800, 80.2800),
                (13.0300, 80.2600),
                (12.9800, 80.2500),
                (12.9100, 80.2400),
            ]
        },
        {
            "name": "Otteri Nullah Channel",
            "type": "URBAN_STORM_DRAIN",
            "capacity_m3s": 180,
            "segments": [
                (13.0950, 80.2200),
                (13.0980, 80.2500),
                (13.0900, 80.2750),
            ]
        },
        {
            "name": "Pallikaranai Wetland Marsh",
            "type": "WETLAND_BASIN",
            "capacity_m3s": 850,
            "segments": [
                (12.9500, 80.2000),
                (12.9300, 80.2200),
                (12.9100, 80.2100),
            ]
        }
    ]

    def __init__(self):
        super().__init__("DrainageProvider", "DERIVED")

    def get_drainage_context(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Alias for get_drainage_features with normalized key names."""
        feats = self.get_drainage_features(latitude, longitude)
        return {
            "nearest_drainage": feats["nearest_drainage"],
            "distance_km": feats["distance_to_drainage_km"],
            "drainage_risk": feats["drainage_risk_score"],
            "bottleneck_risk": feats["hydraulic_bottleneck_warning"],
            "features": feats
        }

    def get_drainage_features(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Calculates distance to closest drainage corridor and hydraulic bottleneck vulnerability.
        """
        min_dist_km = 999.0
        nearest_corridor = None

        for corridor in self.MAJOR_DRAINAGE_CORRIDORS:
            for pt in corridor["segments"]:
                # Haversine distance
                d = self._haversine_km(latitude, longitude, pt[0], pt[1])
                if d < min_dist_km:
                    min_dist_km = d
                    nearest_corridor = corridor

        min_dist_km = round(min_dist_km, 2)
        corridor_name = nearest_corridor["name"] if nearest_corridor else "None"
        corridor_type = nearest_corridor["type"] if nearest_corridor else "UNKNOWN"

        # Drainage risk score (0-100): Proximity within 500m creates severe spillover hazard
        # < 0.3 km: 90-100, 0.3-1.0 km: 60-90, 1.0-3.0 km: 25-60, > 3.0 km: 10
        if min_dist_km <= 0.3:
            drainage_risk = 95.0
        elif min_dist_km <= 1.0:
            drainage_risk = 75.0 - (min_dist_km - 0.3) * 25.0
        elif min_dist_km <= 3.0:
            drainage_risk = 50.0 - (min_dist_km - 1.0) * 15.0
        else:
            drainage_risk = max(10.0, 20.0 - (min_dist_km - 3.0) * 2.0)

        drainage_risk = round(drainage_risk, 1)

        return {
            "nearest_drainage": corridor_name,
            "drainage_type": corridor_type,
            "distance_to_drainage_km": min_dist_km,
            "drainage_risk_score": drainage_risk,
            "hydraulic_bottleneck_warning": min_dist_km < 0.5,
            "source_type": DataSourceType.DERIVED.value,
            "confidence": 0.80,
            "provenance": self.get_provenance()
        }

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_provenance(self) -> Dict[str, Any]:
        return GeospatialProvenance(
            provider_name="DrainageProvider",
            source_type=DataSourceType.DERIVED,
            dataset_name="Chennai Hydrographic Drainage Network (Public Works Department / CMDA Proxy)",
            resolution="Corridor Vector Polyline Proximity",
            confidence=0.80,
            limitations="Based on major known regional water courses; secondary roadside stormwater micro-drains not modeled.",
            citation="Water Resources Department, Government of Tamil Nadu"
        ).to_dict()

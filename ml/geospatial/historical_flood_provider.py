"""
Historical Flood Memory and Prior Disaster Exposure Provider.
Evaluates proximity and historical recurrence risks based on verified historical meteorological disasters.
"""

import math
from typing import Dict, Any, List, Optional
from .provider import BaseGeospatialProvider, DataSourceType, GeospatialProvenance

class HistoricalFloodProvider(BaseGeospatialProvider):
    """
    Historical Flood Intelligence Provider.
    Queries verified historical disaster records and derives spatial historical exposure scores.
    """

    VERIFIED_HISTORICAL_EVENTS = [
        {
            "id": 1,
            "event_name": "December 2015 Catastrophic Chennai Flood",
            "event_date": "2015-12-01",
            "latitude": 13.0200,
            "longitude": 80.2230,
            "severity": "CRITICAL",
            "rainfall_total_mm": 494.0,
            "duration_hours": 48,
            "source": "India Meteorological Department (IMD) / NDMA Post-Disaster Report",
            "description": "Adyar River breach and Chembarambakkam reservoir release causing massive metropolitan inundation."
        },
        {
            "id": 2,
            "event_name": "December 2023 Cyclone Michaung Inundation",
            "event_date": "2023-12-04",
            "latitude": 12.9815,
            "longitude": 80.2180,
            "severity": "CRITICAL",
            "rainfall_total_mm": 220.0,
            "duration_hours": 36,
            "source": "ECMWF ERA5-Land Reanalysis / IMD Chennai Bulletin",
            "description": "Severe cyclonic storm stagnation dumping extreme rainfall over Velachery, Pallikaranai, and Tambaram."
        },
        {
            "id": 3,
            "event_name": "November 2021 Severe Urban Waterlogging",
            "event_date": "2021-11-07",
            "latitude": 13.0418,
            "longitude": 80.2341,
            "severity": "HIGH",
            "rainfall_total_mm": 205.0,
            "duration_hours": 24,
            "source": "Greater Chennai Corporation (GCC) Disaster Assessment",
            "description": "Prolonged northeast monsoon downpour overwhelming urban storm water drains in Central & North Chennai."
        },
        {
            "id": 4,
            "event_name": "December 2016 Cyclone Vardah Storm Inundation",
            "event_date": "2016-12-12",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "severity": "HIGH",
            "rainfall_total_mm": 192.0,
            "duration_hours": 18,
            "source": "Regional Meteorological Centre (RMC) Chennai",
            "description": "Very severe cyclonic storm making landfall over Chennai coast with surge and street inundation."
        }
    ]

    def __init__(self):
        super().__init__("HistoricalFloodProvider", "HISTORICAL_EVENT")

    def get_historical_events_near(self, latitude: float, longitude: float, radius_km: float = 15.0) -> List[Dict[str, Any]]:
        """Return list of nearby historical events."""
        ctx = self.get_historical_context(latitude, longitude, radius_km=radius_km)
        return ctx["nearby_events"]

    def get_historical_context(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        db_events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate historical flood exposure within a radius in kilometers.
        """
        events = db_events if db_events is not None else self.VERIFIED_HISTORICAL_EVENTS

        nearby_events = []
        nearest_event = None
        min_dist = 999.0

        for ev in events:
            dist = self._haversine_km(latitude, longitude, ev["latitude"], ev["longitude"])
            if dist <= radius_km:
                ev_copy = dict(ev)
                ev_copy["distance_km"] = round(dist, 2)
                nearby_events.append(ev_copy)
            if dist < min_dist:
                min_dist = dist
                nearest_event = ev

        # Calculate historical risk score (0-100)
        # Closer proximity to historical flood epicenters indicates recurring catchment vulnerability
        if not nearby_events:
            historical_score = 15.0
            highest_severity = "NONE"
        else:
            # Sort by distance
            nearby_events.sort(key=lambda x: x["distance_km"])
            closest = nearby_events[0]
            severity_weights = {"CRITICAL": 100.0, "HIGH": 75.0, "MODERATE": 50.0, "LOW": 25.0}
            base_score = severity_weights.get(closest.get("severity", "MODERATE"), 50.0)
            
            # Decay score with distance: at 0 km = 100% of base, at 5 km = 50%
            decay = max(0.2, 1.0 - (closest["distance_km"] / 10.0))
            historical_score = round(base_score * decay, 1)
            highest_severity = closest.get("severity", "MODERATE")

        return {
            "historical_event_count": len(nearby_events),
            "nearest_event_name": nearest_event["event_name"] if nearest_event else None,
            "distance_to_nearest_km": round(min_dist, 2) if nearest_event else None,
            "historical_severity": highest_severity,
            "historical_risk_score": historical_score,
            "nearby_events": nearby_events,
            "source_type": DataSourceType.HISTORICAL_EVENT.value,
            "confidence": 0.88,
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
            provider_name="HistoricalFloodProvider",
            source_type=DataSourceType.HISTORICAL_EVENT,
            dataset_name="Verified Historical Chennai Major Inundation Events (2015-2023)",
            resolution="Geocoded Event Epicenters with Disaster Reports",
            confidence=0.88,
            limitations="Limited to 4 major verified historical flood disasters with published municipal and IMD records.",
            citation="India Meteorological Department (IMD) / National Disaster Management Authority (NDMA)"
        ).to_dict()

"""
AI-DisasterGuard — Safe Shelter Optimization & Recommendation Engine
Phase 5.5: Capacity-Aware & Risk-Dampened Evacuation Destination Intelligence
"""

from typing import Dict, Any, List, Optional
from ml.operations import DataProvenance
from ml.operations.team_matching import calculate_haversine_distance

def match_shelters(
    incident: Any,
    shelters: List[Any],
    flood_zones: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluates and recommends safe evacuation shelters based on:
    - Available bed / shelter capacity
    - Approx. geographic distance
    - Facility operational status (OPEN vs NEAR_CAPACITY vs FULL)
    - Flood hazard exposure
    - Clear data provenance (MOCK/REAL/SIMULATION)
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    inc_lat = float(get_val(incident, "latitude", 0.0) or 0.0)
    inc_lon = float(get_val(incident, "longitude", 0.0) or 0.0)

    evaluated_shelters = []

    for shelter in shelters:
        s_id = get_val(shelter, "id")
        name = str(get_val(shelter, "name", f"Shelter #{s_id}"))
        s_lat = float(get_val(shelter, "latitude", 0.0) or 0.0)
        s_lon = float(get_val(shelter, "longitude", 0.0) or 0.0)
        capacity = int(get_val(shelter, "capacity", 100) or 100)
        occupancy = int(get_val(shelter, "current_occupancy", 0) or 0)
        status = str(get_val(shelter, "status", "OPEN")).upper()
        contact = str(get_val(shelter, "contact", "N/A"))
        provenance = str(get_val(shelter, "data_provenance", DataProvenance.MOCK.value))

        available_capacity = max(0, capacity - occupancy)
        occupancy_pct = (occupancy / max(1, capacity)) * 100.0

        # Distance calculation
        dist_km = calculate_haversine_distance(inc_lat, inc_lon, s_lat, s_lon)

        # Distance score (0-100)
        if dist_km <= 2.0:
            dist_score = 100.0
        elif dist_km <= 5.0:
            dist_score = max(70.0, 100.0 - (dist_km - 2.0) * 8.0)
        elif dist_km <= 15.0:
            dist_score = max(30.0, 70.0 - (dist_km - 5.0) * 4.0)
        else:
            dist_score = max(10.0, 30.0 - (dist_km - 15.0))

        # Capacity score (0-100)
        if status == "FULL" or available_capacity <= 0:
            cap_score = 0.0
        elif status == "NEAR_CAPACITY" or occupancy_pct >= 85.0:
            cap_score = 40.0
        else:
            cap_score = min(100.0, 60.0 + (available_capacity / max(1, capacity)) * 40.0)

        # Safety / Flood Risk Exposure (0-100)
        safety_score = 100.0
        in_flood_danger = False
        if flood_zones:
            for zone in flood_zones:
                z_lat = float(get_val(zone, "latitude", 0.0) or 0.0)
                z_lon = float(get_val(zone, "longitude", 0.0) or 0.0)
                z_risk = str(get_val(zone, "risk_level", "LOW")).upper()
                if z_risk in ["CRITICAL", "HIGH"] and calculate_haversine_distance(s_lat, s_lon, z_lat, z_lon) < 1.0:
                    safety_score = 30.0
                    in_flood_danger = True
                    break

        # Composite score
        total_score = round(0.40 * dist_score + 0.40 * cap_score + 0.20 * safety_score, 1)

        reasons = []
        warnings = []

        if available_capacity > 50:
            reasons.append(f"Substantial capacity available ({available_capacity} slots remaining)")
        elif available_capacity > 0:
            reasons.append(f"Limited capacity remaining ({available_capacity} slots)")
        else:
            warnings.append("Facility at MAXIMUM CAPACITY")

        reasons.append(f"Approx. geographic distance: {dist_km} km")

        if in_flood_danger:
            warnings.append("Facility is in close proximity to active high-risk flood zone")

        evaluated_shelters.append({
            "id": s_id,
            "name": name,
            "score": total_score,
            "distance_km": dist_km,
            "distance_label": f"{dist_km} km (Approx. geographic distance)",
            "capacity": capacity,
            "current_occupancy": occupancy,
            "available_capacity": available_capacity,
            "occupancy_pct": round(occupancy_pct, 1),
            "status": status,
            "contact": contact,
            "data_provenance": provenance,
            "reasons": reasons,
            "warnings": warnings,
        })

    evaluated_shelters.sort(key=lambda x: x["score"], reverse=True)

    recommended = evaluated_shelters[0] if evaluated_shelters else None
    alternatives = evaluated_shelters[1:4] if len(evaluated_shelters) > 1 else []

    return {
        "recommended_shelter": recommended,
        "alternative_shelters": alternatives,
        "all_candidates": evaluated_shelters,
    }

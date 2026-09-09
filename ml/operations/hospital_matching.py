"""
AI-DisasterGuard — Medical Emergency Hospital Matching Engine
Phase 5.5: Trauma Capability & Bed Availability Decision Support
"""

from typing import Dict, Any, List, Optional
from ml.operations import DataProvenance
from ml.operations.team_matching import calculate_haversine_distance

def match_hospitals(
    incident: Any,
    hospitals: List[Any],
    priority_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluates and recommends emergency hospitals for incident casualty intake based on:
    - Emergency capacity status (AVAILABLE vs LIMITED vs FULL)
    - Available emergency / trauma beds
    - Approx. geographic distance
    - Medical urgency requirements
    - Data provenance (MOCK/REAL/SIMULATION)
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    inc_lat = float(get_val(incident, "latitude", 0.0) or 0.0)
    inc_lon = float(get_val(incident, "longitude", 0.0) or 0.0)
    is_medical = bool(get_val(priority_info, "is_medical", False))

    evaluated_hospitals = []

    for hospital in hospitals:
        h_id = get_val(hospital, "id")
        name = str(get_val(hospital, "name", f"Hospital #{h_id}"))
        h_lat = float(get_val(hospital, "latitude", 0.0) or 0.0)
        h_lon = float(get_val(hospital, "longitude", 0.0) or 0.0)
        em_cap = str(get_val(hospital, "emergency_capacity", "AVAILABLE")).upper()
        beds = int(get_val(hospital, "available_beds", 10) or 0)
        status = str(get_val(hospital, "status", "AVAILABLE")).upper()
        contact = str(get_val(hospital, "contact", "N/A"))
        provenance = str(get_val(hospital, "data_provenance", DataProvenance.MOCK.value))

        dist_km = calculate_haversine_distance(inc_lat, inc_lon, h_lat, h_lon)

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
        if em_cap == "FULL" or beds <= 0:
            cap_score = 0.0
            suitability = "LOW"
        elif em_cap == "LIMITED" or beds < 5:
            cap_score = 50.0
            suitability = "MEDIUM"
        else:
            cap_score = min(100.0, 70.0 + min(30.0, float(beds) * 2.0))
            suitability = "HIGH"

        # Urgency boost
        urgency_score = 100.0 if (is_medical and suitability == "HIGH") else 80.0

        total_score = round(0.45 * cap_score + 0.40 * dist_score + 0.15 * urgency_score, 1)

        reasons = []
        warnings = []

        if beds >= 10:
            reasons.append(f"Strong emergency capacity ({beds} available beds)")
        elif beds > 0:
            reasons.append(f"Moderate emergency capacity ({beds} available beds)")
        else:
            warnings.append("Hospital at EMERGENCY SATURATION (0 beds available)")

        reasons.append(f"Approx. geographic distance: {dist_km} km")

        if em_cap == "LIMITED":
            warnings.append("Facility operating under LIMITED emergency intake protocol")

        evaluated_hospitals.append({
            "id": h_id,
            "name": name,
            "score": total_score,
            "distance_km": dist_km,
            "distance_label": f"{dist_km} km (Approx. geographic distance)",
            "emergency_capacity": em_cap,
            "available_beds": beds,
            "medical_suitability": suitability,
            "status": status,
            "contact": contact,
            "data_provenance": provenance,
            "reasons": reasons,
            "warnings": warnings,
        })

    evaluated_hospitals.sort(key=lambda x: x["score"], reverse=True)

    recommended = evaluated_hospitals[0] if evaluated_hospitals else None
    alternatives = evaluated_hospitals[1:4] if len(evaluated_hospitals) > 1 else []

    return {
        "recommended_hospital": recommended,
        "alternative_hospitals": alternatives,
        "all_candidates": evaluated_hospitals,
    }

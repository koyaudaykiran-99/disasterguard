"""
AI-DisasterGuard — Rescue Team Capability & Resource Matching Engine
Phase 5.5: Multi-Factor Candidate Scoring & Transparent Rationale
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ml.operations import DataProvenance

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates approximate geographic distance in km using the Haversine formula."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def match_rescue_teams(
    incident: Any,
    teams: List[Any],
    priority_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluates candidate rescue teams for an incident based on:
    - Capability matching (required & preferred)
    - Availability status
    - Approx. geographic distance
    - Current workload
    - Telemetry freshness
    
    Returns primary recommendation, alternatives, and component scores.
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    inc_lat = float(get_val(incident, "latitude", 0.0) or 0.0)
    inc_lon = float(get_val(incident, "longitude", 0.0) or 0.0)
    
    is_trapped = bool(get_val(priority_info, "is_trapped", False))
    is_medical = bool(get_val(priority_info, "is_medical", False))
    
    # Check text if priority_info not supplied
    if not priority_info:
        desc = str(get_val(incident, "description", "")).lower()
        title = str(get_val(incident, "title", "")).lower()
        is_trapped = any(k in desc or k in title for k in ["trapped", "stranded", "roof"])
        is_medical = any(k in desc or k in title for k in ["medical", "injury", "heart", "bleeding"])

    # Determine capabilities
    required_caps = []
    preferred_caps = []
    optional_caps = ["URBAN_RESCUE", "HIGH_WATER"]
    
    if is_trapped:
        required_caps.append("FLOOD_RESCUE")
        preferred_caps.extend(["BOAT_RESCUE", "SEARCH_AND_RESCUE"])
    else:
        required_caps.append("FLOOD_RESCUE")
        preferred_caps.append("SEARCH_AND_RESCUE")
        
    if is_medical:
        required_caps.append("MEDICAL")
        preferred_caps.append("FIRST_AID")
    else:
        optional_caps.append("FIRST_AID")

    # De-duplicate
    required_caps = list(dict.fromkeys(required_caps))
    preferred_caps = [c for c in list(dict.fromkeys(preferred_caps)) if c not in required_caps]

    evaluated_candidates = []
    now = datetime.now(timezone.utc)

    for team in teams:
        team_id = get_val(team, "id")
        team_name = str(get_val(team, "name", f"Team #{team_id}"))
        team_lat = float(get_val(team, "latitude", 0.0) or 0.0)
        team_lon = float(get_val(team, "longitude", 0.0) or 0.0)
        team_status = str(get_val(team, "status", "AVAILABLE")).upper()
        team_caps = [str(c).upper() for c in (get_val(team, "capabilities", []) or [])]
        team_size = int(get_val(team, "team_size", 4) or 4)
        last_updated = get_val(team, "last_updated")
        active_assignments = int(get_val(team, "active_assignments_count", 0) or 0)
        
        # 1. Distance Calculation (Haversine - labeled Approx. geographic distance)
        dist_km = calculate_haversine_distance(inc_lat, inc_lon, team_lat, team_lon)
        if dist_km <= 2.0:
            dist_score = 100.0
        elif dist_km <= 5.0:
            dist_score = max(80.0, 100.0 - (dist_km - 2.0) * 6.0)
        elif dist_km <= 10.0:
            dist_score = max(60.0, 80.0 - (dist_km - 5.0) * 4.0)
        elif dist_km <= 20.0:
            dist_score = max(30.0, 60.0 - (dist_km - 10.0) * 3.0)
        else:
            dist_score = max(10.0, 30.0 - (dist_km - 20.0))
            
        # 2. Capability Matching Score
        req_matched = sum(1 for req in required_caps if req in team_caps)
        pref_matched = sum(1 for pref in preferred_caps if pref in team_caps)
        
        if len(required_caps) == 0:
            cap_score = 85.0
        elif req_matched == len(required_caps):
            cap_score = 80.0 + (20.0 * (pref_matched / max(1, len(preferred_caps))))
        else:
            # Missing one or more required capabilities
            fraction = req_matched / len(required_caps)
            cap_score = fraction * 40.0
            
        # 3. Availability Score
        if team_status == "AVAILABLE":
            avail_score = 100.0
        elif team_status == "EN_ROUTE":
            avail_score = 40.0
        elif team_status in ["BUSY", "ON_SCENE", "DISPATCHED"]:
            avail_score = 20.0
        else:  # OFFLINE, UNAVAILABLE
            avail_score = 0.0
            
        # 4. Workload Score
        if active_assignments == 0:
            workload_score = 100.0
        elif active_assignments == 1:
            workload_score = 60.0
        else:
            workload_score = 20.0
            
        # 5. Freshness Score
        age_minutes = 0.0
        if last_updated:
            try:
                if isinstance(last_updated, str):
                    dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                else:
                    dt = last_updated
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age_minutes = max(0.0, (now - dt).total_seconds() / 60.0)
            except Exception:
                age_minutes = 0.0
                
        if age_minutes <= 5.0:
            freshness_score = 100.0
        elif age_minutes <= 15.0:
            freshness_score = 85.0
        else:
            freshness_score = max(40.0, 85.0 - (age_minutes - 15.0) * 1.5)
            
        # Composite Suitability Score (0-100)
        overall_score = (
            0.35 * cap_score +
            0.25 * avail_score +
            0.20 * dist_score +
            0.10 * workload_score +
            0.10 * freshness_score
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)
        
        # Candidate Warnings & Reasons
        cand_reasons = []
        cand_warnings = []
        
        if req_matched == len(required_caps) and len(required_caps) > 0:
            cand_reasons.append(f"All required capabilities verified ({', '.join(required_caps)})")
        elif req_matched > 0:
            cand_warnings.append(f"Partial capability match ({req_matched}/{len(required_caps)} required)")
        else:
            cand_warnings.append(f"Missing required capabilities: {', '.join(required_caps)}")
            
        if dist_km <= 3.0:
            cand_reasons.append(f"Closest available team ({dist_km} km approx. geographic distance)")
        else:
            cand_reasons.append(f"Approx. geographic distance: {dist_km} km")
            
        if team_status == "AVAILABLE":
            cand_reasons.append("Team currently AVAILABLE for deployment")
        else:
            cand_warnings.append(f"Team status is {team_status} (workload: {active_assignments} active)")
            
        if age_minutes > 15.0:
            cand_warnings.append(f"Location update is {int(age_minutes)} minutes old")
            
        candidate_data = {
            "id": team_id,
            "name": team_name,
            "score": overall_score,
            "status": team_status,
            "distance_km": dist_km,
            "distance_label": f"{dist_km} km (Approx. geographic distance)",
            "capabilities": team_caps,
            "team_size": team_size,
            "workload": active_assignments,
            "telemetry_age_minutes": round(age_minutes, 1),
            "data_provenance": DataProvenance.CACHED.value if age_minutes > 5.0 else DataProvenance.REAL.value,
            "component_scores": {
                "capability": round(cap_score, 1),
                "availability": round(avail_score, 1),
                "distance": round(dist_score, 1),
                "workload": round(workload_score, 1),
                "freshness": round(freshness_score, 1),
            },
            "reasons": cand_reasons,
            "warnings": cand_warnings,
        }
        evaluated_candidates.append(candidate_data)

    # Sort by score descending
    evaluated_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    primary = evaluated_candidates[0] if evaluated_candidates else None
    alternatives = evaluated_candidates[1:4] if len(evaluated_candidates) > 1 else []
    
    return {
        "required_capabilities": required_caps,
        "preferred_capabilities": preferred_caps,
        "recommended_team": primary,
        "alternative_teams": alternatives,
        "all_candidates": evaluated_candidates,
    }

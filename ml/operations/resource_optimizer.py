"""
AI-DisasterGuard — Multi-Incident Resource Optimizer & Contention Detection
Phase 5.5: Multi-Emergency Coordination & Decision Support (Zero Auto-Dispatch)
"""

from typing import Dict, Any, List, Optional
from ml.operations import (
    ContentionSeverity,
    OperationalPriorityLevel,
)
from ml.operations.incident_priority import calculate_incident_priority
from ml.operations.team_matching import match_rescue_teams
from ml.operations.shelter_matching import match_shelters
from ml.operations.hospital_matching import match_hospitals

def optimize_disaster_operations(
    incidents: List[Any],
    teams: List[Any],
    shelters: Optional[List[Any]] = None,
    hospitals: Optional[List[Any]] = None,
    triage_map: Optional[Dict[int, Any]] = None,
    forecast_map: Optional[Dict[int, Any]] = None,
    flood_map: Optional[Dict[int, Any]] = None,
) -> Dict[str, Any]:
    """
    Coordinates multi-incident emergency operations:
    1. Computes explainable operational priority (0-100) for all active incidents.
    2. Discovers candidate rescue teams, shelters, and hospitals.
    3. Detects Resource Contention when multiple emergencies compete for the same rescue team.
    4. Ranks precedence by operational priority score and suggests alternatives.
    5. SAFETY INVARIANT: Never performs autonomous dispatch or reassignment.
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    triage_map = triage_map or {}
    forecast_map = forecast_map or {}
    flood_map = flood_map or {}
    shelters = shelters or []
    hospitals = hospitals or []

    scored_incidents = []

    # 1. Prioritize each incident and evaluate candidate matches
    for inc in incidents:
        inc_id = get_val(inc, "id")
        triage = triage_map.get(inc_id)
        forecast = forecast_map.get(inc_id)
        flood = flood_map.get(inc_id)

        # Operational Priority
        p_info = calculate_incident_priority(inc, triage, forecast, flood)

        # Team Matching
        team_info = match_rescue_teams(inc, teams, p_info)

        # Shelter Matching
        shelter_info = match_shelters(inc, shelters)

        # Hospital Matching
        hospital_info = match_hospitals(inc, hospitals, p_info)

        scored_incidents.append({
            "incident": inc,
            "incident_id": inc_id,
            "priority_info": p_info,
            "team_info": team_info,
            "shelter_info": shelter_info,
            "hospital_info": hospital_info,
            "contention": None,
        })

    # Sort incidents descending by operational priority score
    scored_incidents.sort(key=lambda x: x["priority_info"]["priority_score"], reverse=True)

    # 2. Resource Contention Detection
    # Group by recommended team id
    team_usage_map: Dict[int, List[Dict[str, Any]]] = {}
    for item in scored_incidents:
        rec_team = item["team_info"]["recommended_team"]
        if rec_team:
            t_id = rec_team["id"]
            team_usage_map.setdefault(t_id, []).append(item)

    detected_contentions = []

    for t_id, contending_items in team_usage_map.items():
        if len(contending_items) > 1:
            # Resource Contention Detected!
            team_name = contending_items[0]["team_info"]["recommended_team"]["name"]
            
            # contending_items is already sorted by priority_score descending
            winner_item = contending_items[0]
            winner_id = winner_item["incident_id"]
            winner_score = winner_item["priority_info"]["priority_score"]
            
            contending_ids = [it["incident_id"] for it in contending_items]
            
            # Determine severity
            scores = [it["priority_info"]["priority_score"] for it in contending_items]
            if all(s >= 70.0 for s in scores):
                contention_sev = ContentionSeverity.CRITICAL.value
            elif any(s >= 70.0 for s in scores):
                contention_sev = ContentionSeverity.HIGH.value
            else:
                contention_sev = ContentionSeverity.MODERATE.value

            # Format comprehensive explanation
            desc_lines = [
                f"Resource Contention Detected for {team_name} across {len(contending_items)} active incidents: #{', #'.join(str(i) for i in contending_ids)}.",
                f"Incident #{winner_id} takes precedence with operational priority {winner_score}/100."
            ]
            if winner_item["priority_info"]["reasons"]:
                desc_lines.append(f"Precedence rationale: {'; '.join(winner_item['priority_info']['reasons'])}.")

            contention_record = {
                "resource_id": t_id,
                "resource_name": team_name,
                "incident_ids": contending_ids,
                "preferred_incident_id": winner_id,
                "severity": contention_sev,
                "description": " ".join(desc_lines),
                "contending_incidents_detail": [
                    {
                        "incident_id": it["incident_id"],
                        "priority_score": it["priority_info"]["priority_score"],
                        "priority_level": it["priority_info"]["priority_level"],
                        "reasons": it["priority_info"]["reasons"],
                    }
                    for it in contending_items
                ]
            }
            detected_contentions.append(contention_record)

            # Mark contention on the lower-priority incidents and designate suggested alternative
            for idx, item in enumerate(contending_items):
                if idx == 0:
                    # Winner retains primary recommendation with a note about contention
                    item["contention"] = {
                        "is_contended": True,
                        "status": "PRIMARY_CLAIM",
                        "team_id": t_id,
                        "team_name": team_name,
                        "competing_incident_ids": contending_ids[1:],
                        "note": f"Incident has primary priority claim over {team_name}."
                    }
                else:
                    # Secondary incident has contention flag and alternative suggestion
                    alts = item["team_info"]["alternative_teams"]
                    suggested_alt = alts[0] if alts else None
                    alt_name = suggested_alt["name"] if suggested_alt else "None available"
                    
                    item["contention"] = {
                        "is_contended": True,
                        "status": "CONTENTION_CONFLICT",
                        "team_id": t_id,
                        "team_name": team_name,
                        "priority_claim_incident_id": winner_id,
                        "explanation": f"{team_name} is also recommended for higher-priority Incident #{winner_id} (Score {winner_score}). Suggested alternative: {alt_name}.",
                        "suggested_alternative_team": suggested_alt,
                    }
                    item["team_info"]["recommended_team"]["contention_warning"] = (
                        f"Contended resource: Precedence given to Incident #{winner_id}"
                    )

    return {
        "prioritized_incidents": scored_incidents,
        "contentions": detected_contentions,
        "total_active_incidents": len(incidents),
        "contentions_count": len(detected_contentions),
    }

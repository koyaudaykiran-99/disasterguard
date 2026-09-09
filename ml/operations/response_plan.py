"""
AI-DisasterGuard — Unified Response Plan Generator
Phase 5.5: Coordinated Action Packaging with Inviolate Human Confirmation Barrier
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ml.operations import DataProvenance, OperationalStatus

def generate_response_plan(
    incident: Any,
    priority_info: Dict[str, Any],
    team_matching: Dict[str, Any],
    shelter_matching: Optional[Dict[str, Any]] = None,
    hospital_matching: Optional[Dict[str, Any]] = None,
    contention_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Synthesizes multi-resource operational evaluations into a unified Response Plan.
    
    CRITICAL INVARIANT:
    - human_confirmation_required is ALWAYS True.
    - AI recommendations provide decision support and CANNOT perform autonomous dispatch.
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    inc_id = get_val(incident, "id")
    p_score = float(priority_info.get("priority_score", 0.0))
    p_level = priority_info.get("priority_level", "LOW")
    
    rec_team = team_matching.get("recommended_team")
    alt_teams = team_matching.get("alternative_teams", [])
    
    rec_shelter = shelter_matching.get("recommended_shelter") if shelter_matching else None
    rec_hospital = hospital_matching.get("recommended_hospital") if hospital_matching else None

    # Synthesize reasons
    reasons: List[str] = []
    if priority_info.get("reasons"):
        reasons.extend(priority_info["reasons"])
    if rec_team and rec_team.get("reasons"):
        reasons.extend(rec_team["reasons"][:2])
    if rec_shelter and rec_shelter.get("reasons"):
        reasons.append(f"Shelter: {rec_shelter['name']} ({rec_shelter['reasons'][0]})")
    if rec_hospital and rec_hospital.get("reasons"):
        reasons.append(f"Hospital: {rec_hospital['name']} ({rec_hospital['reasons'][0]})")

    # Synthesize warnings
    warnings: List[str] = []
    if priority_info.get("warnings"):
        warnings.extend(priority_info["warnings"])
    if rec_team and rec_team.get("warnings"):
        warnings.extend(rec_team["warnings"])
    if rec_shelter and rec_shelter.get("warnings"):
        warnings.extend(rec_shelter["warnings"])
    if rec_hospital and rec_hospital.get("warnings"):
        warnings.extend(rec_hospital["warnings"])
    if contention_info and contention_info.get("is_contended"):
        warnings.append(f"Resource Contention: {contention_info.get('explanation', 'Team contended across multiple incidents')}")

    # Confidence estimation
    if rec_team and rec_team["score"] >= 80.0 and len(warnings) <= 1:
        confidence = "HIGH"
    elif rec_team and rec_team["score"] >= 50.0:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # Data Provenance mapping
    provenance = {
        "incident": DataProvenance.REAL.value,
        "priority_score": DataProvenance.DERIVED.value,
        "recommended_team": rec_team.get("data_provenance", DataProvenance.CACHED.value) if rec_team else DataProvenance.REAL.value,
        "recommended_shelter": rec_shelter.get("data_provenance", DataProvenance.MOCK.value) if rec_shelter else DataProvenance.MOCK.value,
        "recommended_hospital": rec_hospital.get("data_provenance", DataProvenance.MOCK.value) if rec_hospital else DataProvenance.MOCK.value,
    }

    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "incident_id": inc_id,
        "priority": p_level,
        "priority_score": p_score,
        "recommended_team": rec_team,
        "alternative_teams": alt_teams,
        "recommended_shelter": rec_shelter,
        "recommended_hospital": rec_hospital,
        "contention": contention_info,
        "reasons": list(dict.fromkeys(reasons)),
        "warnings": list(dict.fromkeys(warnings)),
        "confidence": confidence,
        "data_provenance": provenance,
        "status": OperationalStatus.RECOMMENDED.value,
        "human_confirmation_required": True,
        "created_at": now_iso,
    }

"""
AI-DisasterGuard — Operational Analytics & Resource Metrics Engine
Phase 5.5: Stored-Data Driven Operational Telemetry (Strictly Honest, No Fabrications)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def calculate_operational_metrics(
    incidents: List[Any],
    teams: List[Any],
    shelters: List[Any],
    hospitals: List[Any],
    contentions: Optional[List[Any]] = None,
    bottlenecks: Optional[List[Any]] = None,
    audit_logs: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Computes system-wide operational metrics derived exclusively from stored entity states.
    Honesty Rule: Does NOT claim unverified response time percentage reductions or fabricated metrics.
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    contentions = contentions or []
    bottlenecks = bottlenecks or []
    audit_logs = audit_logs or []

    # 1. Incident Metrics
    total_incidents = len(incidents)
    active_incidents = 0
    critical_incidents = 0
    high_priority_incidents = 0
    unassigned_incidents = 0
    dispatched_incidents = 0
    resolved_incidents = 0
    total_age_minutes = 0.0
    now = datetime.now(timezone.utc)

    for inc in incidents:
        st = str(get_val(inc, "status", "PENDING")).upper()
        sev = str(get_val(inc, "severity", "LOW")).upper()
        p_score = float(get_val(inc, "priority_score", 0.0) or 0.0)

        if st in ["PENDING", "DISPATCHED", "UNASSIGNED", "EN_ROUTE"]:
            active_incidents += 1
        if st == "RESOLVED":
            resolved_incidents += 1
        elif st in ["PENDING", "UNASSIGNED"]:
            unassigned_incidents += 1
        elif st in ["DISPATCHED", "EN_ROUTE"]:
            dispatched_incidents += 1

        if p_score >= 90.0 or sev == "CRITICAL":
            critical_incidents += 1
        elif p_score >= 70.0 or sev == "HIGH":
            high_priority_incidents += 1

        c_at = get_val(inc, "created_at")
        if c_at:
            try:
                if isinstance(c_at, str):
                    dt = datetime.fromisoformat(c_at.replace("Z", "+00:00"))
                else:
                    dt = c_at
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age = max(0.0, (now - dt).total_seconds() / 60.0)
                total_age_minutes += age
            except Exception:
                pass

    avg_incident_age_minutes = round(total_age_minutes / max(1, total_incidents), 1) if total_incidents > 0 else 0.0

    # 2. Rescue Team Metrics
    total_teams = len(teams)
    available_teams = 0
    busy_teams = 0
    en_route_teams = 0
    on_scene_teams = 0
    offline_teams = 0

    for t in teams:
        t_st = str(get_val(t, "status", "AVAILABLE")).upper()
        if t_st == "AVAILABLE":
            available_teams += 1
        elif t_st == "EN_ROUTE":
            en_route_teams += 1
            busy_teams += 1
        elif t_st in ["ON_SCENE", "BUSY", "DISPATCHED"]:
            on_scene_teams += 1
            busy_teams += 1
        else:
            offline_teams += 1

    team_utilization_rate = round((busy_teams / max(1, total_teams)) * 100.0, 1) if total_teams > 0 else 0.0

    # 3. Shelter Metrics
    shelter_cap = sum(int(get_val(s, "capacity", 0) or 0) for s in shelters)
    shelter_occ = sum(int(get_val(s, "current_occupancy", 0) or 0) for s in shelters)
    shelter_avail = max(0, shelter_cap - shelter_occ)
    shelter_util_pct = round((shelter_occ / max(1, shelter_cap)) * 100.0, 1) if shelter_cap > 0 else 0.0

    # 4. Hospital Metrics
    hosp_beds = sum(int(get_val(h, "available_beds", 0) or 0) for h in hospitals)
    saturated_hospitals = sum(
        1 for h in hospitals
        if str(get_val(h, "emergency_capacity", "")).upper() == "FULL" or int(get_val(h, "available_beds", 0) or 0) == 0
    )

    # 5. Audit Latency (Real, from timestamps)
    review_latencies = []
    for log in audit_logs:
        action = str(get_val(log, "action", "")).upper()
        # If latency is tracked or calculated from matching created_at / confirmed_at
        lat = get_val(log, "review_latency_seconds")
        if lat is not None:
            review_latencies.append(float(lat))

    avg_review_latency = round(sum(review_latencies) / max(1, len(review_latencies)), 1) if review_latencies else None

    return {
        "active_incidents": active_incidents,
        "critical_incidents": critical_incidents,
        "high_priority_incidents": high_priority_incidents,
        "unassigned_incidents": unassigned_incidents,
        "dispatched_incidents": dispatched_incidents,
        "resolved_incidents": resolved_incidents,
        "total_incidents": total_incidents,
        "avg_incident_age_minutes": avg_incident_age_minutes,
        "teams_available": available_teams,
        "teams_busy": busy_teams,
        "teams_en_route": en_route_teams,
        "teams_on_scene": on_scene_teams,
        "teams_offline": offline_teams,
        "total_teams": total_teams,
        "resource_utilization_pct": team_utilization_rate,
        "shelter_total_capacity": shelter_cap,
        "shelter_total_occupancy": shelter_occ,
        "shelter_available_capacity": shelter_avail,
        "shelter_utilization_pct": shelter_util_pct,
        "hospital_available_beds": hosp_beds,
        "saturated_hospitals_count": saturated_hospitals,
        "total_hospitals": len(hospitals),
        "active_contentions_count": len(contentions),
        "active_bottlenecks_count": len(bottlenecks),
        "avg_review_latency_seconds": avg_review_latency,
        "provenance": {
            "source": "STORED_DATABASE_ENTITIES",
            "mode": "TRANSPARENT_OBSERVATION",
        }
    }

"""
AI-DisasterGuard — Operational Bottleneck & System Saturation Detector
Phase 5.5: Coverage Gaps, Resource Shortages, and Facility Overload Intelligence
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ml.operations import BottleneckType, ContentionSeverity
from ml.operations.team_matching import calculate_haversine_distance

def detect_operational_bottlenecks(
    incidents: List[Any],
    teams: List[Any],
    shelters: List[Any],
    hospitals: List[Any],
    zone: str = "District Operational Area",
) -> List[Dict[str, Any]]:
    """
    Scans the regional disaster response theater for operational bottlenecks:
    1. Rescue Squad Shortage: Available teams < high-priority active incidents.
    2. Shelter Shortage: Cumulative occupancy > 85% or available capacity < 50.
    3. Hospital Overload: Cumulative available trauma beds < 10 or facility saturation.
    4. Stale Telemetry: Rescue teams operating with location updates > 15 min old.
    5. Coverage Gaps: Critical incidents with no suitable rescue squad within 15 km.
    """
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    bottlenecks: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    # 1. Rescue Shortage Analysis
    available_teams = [t for t in teams if str(get_val(t, "status", "")).upper() == "AVAILABLE"]
    urgent_incidents = [
        inc for inc in incidents
        if str(get_val(inc, "severity", "")).upper() in ["CRITICAL", "HIGH"] or
           float(get_val(inc, "priority_score", 0.0) or 0.0) >= 70.0
    ]

    if len(urgent_incidents) > len(available_teams):
        deficit = len(urgent_incidents) - len(available_teams)
        sev = ContentionSeverity.CRITICAL.value if len(available_teams) == 0 else ContentionSeverity.HIGH.value
        bottlenecks.append({
            "zone": zone,
            "bottleneck_type": BottleneckType.RESCUE_SHORTAGE.value,
            "severity": sev,
            "description": f"Rescue squad deficit: {len(urgent_incidents)} urgent incidents competing for {len(available_teams)} available rescue teams (Shortfall of {deficit} teams).",
            "metrics": {
                "urgent_incidents_count": len(urgent_incidents),
                "available_teams_count": len(available_teams),
                "deficit": deficit,
            },
            "guidance": "Request mutual aid from neighboring districts or re-prioritize standby squads.",
        })

    # 2. Shelter Capacity Saturation
    total_shelter_cap = sum(int(get_val(s, "capacity", 0) or 0) for s in shelters)
    total_shelter_occ = sum(int(get_val(s, "current_occupancy", 0) or 0) for s in shelters)
    shelter_avail = max(0, total_shelter_cap - total_shelter_occ)
    shelter_pct = (total_shelter_occ / max(1, total_shelter_cap)) * 100.0 if total_shelter_cap > 0 else 0.0

    if shelter_pct >= 85.0 or (total_shelter_cap > 0 and shelter_avail < 50):
        sev = ContentionSeverity.CRITICAL.value if shelter_pct >= 95.0 else ContentionSeverity.HIGH.value
        bottlenecks.append({
            "zone": zone,
            "bottleneck_type": BottleneckType.SHELTER_SHORTAGE.value,
            "severity": sev,
            "description": f"Shelter capacity saturation: Facility occupancy has reached {shelter_pct:.1f}% with only {shelter_avail} spaces remaining across {len(shelters)} shelters.",
            "metrics": {
                "total_capacity": total_shelter_cap,
                "current_occupancy": total_shelter_occ,
                "available_spaces": shelter_avail,
                "occupancy_pct": round(shelter_pct, 1),
            },
            "guidance": "Designate secondary emergency relief shelters or open civic centers.",
        })

    # 3. Hospital Overload
    total_beds = sum(int(get_val(h, "available_beds", 0) or 0) for h in hospitals)
    full_hospitals = [
        h for h in hospitals
        if str(get_val(h, "emergency_capacity", "")).upper() == "FULL" or int(get_val(h, "available_beds", 0) or 0) == 0
    ]

    if total_beds < 10 or len(full_hospitals) > 0:
        sev = ContentionSeverity.CRITICAL.value if total_beds < 5 else ContentionSeverity.HIGH.value
        bottlenecks.append({
            "zone": zone,
            "bottleneck_type": BottleneckType.HOSPITAL_OVERLOAD.value,
            "severity": sev,
            "description": f"Hospital intake strain: Only {total_beds} emergency trauma beds available across {len(hospitals)} facilities ({len(full_hospitals)} saturated).",
            "metrics": {
                "available_beds": total_beds,
                "saturated_hospitals_count": len(full_hospitals),
                "total_facilities": len(hospitals),
            },
            "guidance": "Coordinate triage diversion protocols and activate field medical stabilization units.",
        })

    # 4. Stale Telemetry Detection
    stale_teams = []
    for t in teams:
        l_up = get_val(t, "last_updated")
        if l_up:
            try:
                if isinstance(l_up, str):
                    dt = datetime.fromisoformat(l_up.replace("Z", "+00:00"))
                else:
                    dt = l_up
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age_min = (now - dt).total_seconds() / 60.0
                if age_min > 15.0:
                    stale_teams.append({
                        "id": get_val(t, "id"),
                        "name": get_val(t, "name"),
                        "age_minutes": round(age_min, 1)
                    })
            except Exception:
                pass

    if stale_teams:
        bottlenecks.append({
            "zone": zone,
            "bottleneck_type": BottleneckType.STALE_TELEMETRY.value,
            "severity": ContentionSeverity.MODERATE.value,
            "description": f"Degraded location telemetry: {len(stale_teams)} rescue squad(s) have GPS updates older than 15 minutes.",
            "metrics": {
                "stale_teams": stale_teams,
                "stale_count": len(stale_teams),
            },
            "guidance": "Request VHF radio or cellular telemetry refresh from field personnel.",
        })

    # 5. Coverage Gap Analysis
    coverage_gaps = []
    for inc in urgent_incidents:
        i_lat = float(get_val(inc, "latitude", 0.0) or 0.0)
        i_lon = float(get_val(inc, "longitude", 0.0) or 0.0)
        closest_dist = min(
            (calculate_haversine_distance(i_lat, i_lon, float(get_val(t, "latitude", 0.0)), float(get_val(t, "longitude", 0.0)))
             for t in available_teams),
            default=999.0
        )
        if closest_dist > 15.0:
            coverage_gaps.append({
                "incident_id": get_val(inc, "id"),
                "title": get_val(inc, "title"),
                "closest_team_dist_km": closest_dist,
            })

    if coverage_gaps:
        bottlenecks.append({
            "zone": zone,
            "bottleneck_type": BottleneckType.COVERAGE_GAP.value,
            "severity": ContentionSeverity.CRITICAL.value if any(g["closest_team_dist_km"] > 25.0 for g in coverage_gaps) else ContentionSeverity.HIGH.value,
            "description": f"Geographic coverage gap: {len(coverage_gaps)} high-priority emergency(s) have no available rescue squads within 15 km.",
            "metrics": {
                "gap_incidents": coverage_gaps,
                "gap_count": len(coverage_gaps),
            },
            "guidance": "Forward-deploy regional standby assets closer to affected sectors.",
        })

    return bottlenecks

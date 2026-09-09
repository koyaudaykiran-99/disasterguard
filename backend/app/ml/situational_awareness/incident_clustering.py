"""
AI-DisasterGuard — Incident Cluster Intelligence
Phase 6: Spatial Incident Aggregation, Resource Demand Synthesis, and Cluster Scoring
"""

import math
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.gis.spatial_queries import haversine_distance_km

logger = logging.getLogger("disasterguard.ml.situational_awareness.incident_clustering")


class IncidentClusterer:
    """
    Synthesizes geographic clusters of active emergencies.
    Does NOT merge emergency records; maintains reference pointers and aggregate telemetry.
    """

    def __init__(self, max_cluster_radius_km: float = 2.5):
        self.max_cluster_radius_km = max_cluster_radius_km

    def cluster_incidents(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups incidents within geographic proximity into explainable disaster clusters.
        """
        clusters: List[Dict[str, Any]] = []
        if not incidents:
            return clusters

        assigned = set()
        cluster_idx = 1

        for i, root_inc in enumerate(incidents):
            root_id = root_inc.get("id")
            if root_id in assigned:
                continue

            root_lat = float(root_inc.get("latitude", 0.0))
            root_lng = float(root_inc.get("longitude", 0.0))

            group = [root_inc]
            assigned.add(root_id)

            for j, candidate in enumerate(incidents):
                cand_id = candidate.get("id")
                if cand_id in assigned:
                    continue

                c_lat = float(candidate.get("latitude", 0.0))
                c_lng = float(candidate.get("longitude", 0.0))

                dist = haversine_distance_km(root_lat, root_lng, c_lat, c_lng)
                if dist <= self.max_cluster_radius_km:
                    group.append(candidate)
                    assigned.add(cand_id)

            # Compute cluster centroid and aggregate metrics
            avg_lat = sum(float(x.get("latitude", 0.0)) for x in group) / len(group)
            avg_lng = sum(float(x.get("longitude", 0.0)) for x in group) / len(group)

            # Severity distribution
            sev_dist: Dict[str, int] = {}
            for item in group:
                s = str(item.get("severity", "HIGH")).upper()
                sev_dist[s] = sev_dist.get(s, 0) + 1

            # Estimated affected population proxy
            total_people = sum(int(x.get("people_at_risk") or x.get("people_count") or 1) for x in group)

            # Dominant hazard & required capabilities
            has_trapped = any(bool(x.get("is_trapped")) or "TRAP" in str(x.get("emergency_type", "")).upper() for x in group)
            has_medical = any(bool(x.get("is_medical")) or "MED" in str(x.get("emergency_type", "")).upper() for x in group)

            capabilities_needed = ["FLOOD_RESCUE"]
            if has_trapped:
                capabilities_needed.append("BOAT_RESCUE")
            if has_medical:
                capabilities_needed.append("EMERGENCY_MEDICAL")

            risk_level = "CRITICAL" if sev_dist.get("CRITICAL", 0) > 0 or len(group) >= 3 else "HIGH"
            cluster_code = f"CLUSTER-{datetime.now(timezone.utc).strftime('%m%d')}-{cluster_idx:03d}"

            attention = (
                f"Multi-incident cluster with {len(group)} active emergencies. "
                f"Requires coordination of {', '.join(capabilities_needed)}."
            )

            clusters.append({
                "cluster_code": cluster_code,
                "title": f"Incident Cluster #{cluster_idx:03d} ({len(group)} Emergencies)",
                "dominant_hazard": "FLOOD",
                "risk_level": risk_level,
                "latitude": round(avg_lat, 5),
                "longitude": round(avg_lng, 5),
                "radius_km": round(self.max_cluster_radius_km, 2),
                "incident_count": len(group),
                "incident_ids": [x.get("id") for x in group],
                "severity_distribution": sev_dist,
                "estimated_affected_population": total_people,
                "resource_demand": {
                    "required_capabilities": capabilities_needed,
                    "recommended_teams_count": max(1, math.ceil(len(group) / 2)),
                    "requires_medical": has_medical,
                    "requires_boats": has_trapped,
                },
                "recommended_attention": attention,
                "confidence": 0.88,
                "is_active": True,
            })
            cluster_idx += 1

        return clusters

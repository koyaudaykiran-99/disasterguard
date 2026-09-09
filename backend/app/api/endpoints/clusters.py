"""
AI-DisasterGuard — Incident Clusters API Endpoints
Phase 6: Spatial Incident Aggregation and Resource Demand Synthesis
"""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.situational_awareness import IncidentCluster
from app.services.situational_awareness_service import situational_awareness_service
from app.schemas.situational_awareness import IncidentClusterResponse

router = APIRouter()


@router.get("/", response_model=List[IncidentClusterResponse])
def list_incident_clusters(db: Session = Depends(get_db)):
    """
    Returns active spatial incident clusters.
    Groups co-located emergencies and synthesizes resource demands without merging emergency records.
    """
    try:
        return situational_awareness_service.get_incident_clusters(db, active_only=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incident clusters: {str(e)}")


@router.get("/{cluster_id}", response_model=IncidentClusterResponse)
def get_incident_cluster_detail(cluster_id: int, db: Session = Depends(get_db)):
    """Returns granular composition and resource demands for a specific incident cluster."""
    cluster = db.query(IncidentCluster).filter(IncidentCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail=f"Incident cluster #{cluster_id} not found")

    return {
        "id": cluster.id,
        "cluster_code": cluster.cluster_code,
        "title": cluster.title,
        "dominant_hazard": cluster.dominant_hazard,
        "risk_level": cluster.risk_level,
        "latitude": cluster.latitude,
        "longitude": cluster.longitude,
        "radius_km": cluster.radius_km,
        "incident_count": cluster.incident_count,
        "incident_ids": json.loads(cluster.incident_ids_json or "[]"),
        "severity_distribution": json.loads(cluster.severity_distribution_json or "{}"),
        "estimated_affected_population": cluster.estimated_affected_population,
        "resource_demand": json.loads(cluster.resource_demand_json or "{}"),
        "recommended_attention": cluster.recommended_attention,
        "confidence": cluster.confidence,
        "is_active": cluster.is_active,
        "detected_at": cluster.detected_at.isoformat() if cluster.detected_at else "",
    }

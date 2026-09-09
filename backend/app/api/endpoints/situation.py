"""
AI-DisasterGuard — Situational Awareness API Endpoints
Phase 6: Real-time situation snapshots, detected changes, and situational history
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.database import get_db
from app.database.models.situational_awareness import SituationalSnapshot
from app.services.situational_awareness_service import situational_awareness_service
from app.schemas.situational_awareness import (
    SituationalSnapshotResponse,
    RecentChangesResponse,
)

router = APIRouter()


@router.get("/current", response_model=SituationalSnapshotResponse)
def get_current_situation(db: Session = Depends(get_db)):
    """
    Returns current multi-signal operational situation snapshot.
    Combines meteorological feeds, ML forecasts, flood zones, active emergencies, and facility capacities.
    """
    try:
        return situational_awareness_service.get_current_situation(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute situational snapshot: {str(e)}")


@router.get("/changes", response_model=RecentChangesResponse)
def get_recent_changes(
    limit: int = Query(20, ge=1, le=100),
    minutes: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns recent operational delta events across all sectors with freshness indicators.
    """
    try:
        changes = situational_awareness_service.get_recent_changes(db, limit=limit)
        gen_time = changes[0]["timestamp"] if changes else ""
        return {
            "status": "SUCCESS",
            "changes_count": len(changes),
            "count": len(changes),
            "changes": changes,
            "recent_changes": changes,
            "generated_at": gen_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent changes: {str(e)}")


@router.get("/history", response_model=List[SituationalSnapshotResponse])
def get_situational_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Returns historical situational snapshots for longitudinal trend analysis.
    """
    try:
        snaps = db.query(SituationalSnapshot).order_by(desc(SituationalSnapshot.generated_at)).limit(limit).all()
        results = []
        for s in snaps:
            import json
            results.append({
                "id": s.id,
                "overall_status": s.overall_status,
                "risk_score": s.risk_score,
                "risk_direction": s.risk_direction,
                "critical_areas": json.loads(s.critical_areas_json or "[]"),
                "active_incidents": s.active_incidents,
                "critical_incidents": s.critical_incidents,
                "active_alerts": s.active_alerts,
                "resource_contentions": s.resource_contentions,
                "operational_bottlenecks": s.operational_bottlenecks,
                "recommended_operator_attention": json.loads(s.recommended_operator_attention_json or "[]"),
                "confidence": s.confidence,
                "data_freshness": json.loads(s.data_freshness_json or "{}"),
                "data_provenance": s.data_provenance,
                "generated_at": s.generated_at.isoformat() if s.generated_at else "",
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch situational history: {str(e)}")

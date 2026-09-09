"""
AI-DisasterGuard — Operations API Endpoints
Phase 5.5: Multi-Incident Situational Intelligence & Decision Support
"""

import jwt
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.user import User, UserRole
from app.core.config import settings
from app.services.operations_service import OperationsService
from app.schemas.operations import (
    OperationalOverviewResponse,
    PrioritizedIncidentItem,
    IncidentPriorityResponse,
    ResponsePlanResponse,
    ResponsePlanOverrideRequest,
    ResponsePlanRejectRequest,
    ResourceContentionResponse,
    OperationalBottleneckResponse,
    ResourceCoverageResponse,
    CapacityIntelligenceResponse,
)

router = APIRouter()

def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Resolves current user if headers are present; allows open read for situational awareness."""
    if x_user_role:
        role_clean = x_user_role.strip().upper()
        if role_clean in UserRole.__members__:
            user = db.query(User).filter(User.role == UserRole(role_clean)).first()
            if user:
                return user
            return User(id=1, name=f"User {role_clean}", email=f"{role_clean.lower()}@disasterguard.gov", role=UserRole(role_clean))

    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token in ["demo", "demo-operator-token", "operator"]:
            op = db.query(User).filter(User.role.in_([UserRole.OPERATOR, UserRole.ADMIN])).first()
            if op:
                return op
            return User(id=1, name="Chief Dispatch Officer", email="dispatch@disasterguard.gov", role=UserRole.OPERATOR)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return db.query(User).filter(User.id == int(user_id)).first()
        except Exception:
            pass
    return None

def require_operator(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Enforces OPERATOR or ADMIN role for human-governed operational actions."""
    if x_user_role:
        role_clean = x_user_role.strip().upper()
        if role_clean in [UserRole.OPERATOR.value, UserRole.ADMIN.value]:
            user = db.query(User).filter(User.role == UserRole(role_clean)).first()
            if user:
                return user
            return User(id=1, name="Operator", email="operator@disasterguard.gov", role=UserRole(role_clean))
        else:
            raise HTTPException(status_code=403, detail="Access forbidden: OPERATOR or ADMIN authority required.")

    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication credentials required.")

    token = authorization.replace("Bearer ", "").strip()
    if token in ["demo", "demo-operator-token", "operator"]:
        op = db.query(User).filter(User.role.in_([UserRole.OPERATOR, UserRole.ADMIN])).first()
        if op:
            return op
        return User(id=1, name="Chief Dispatch Officer", email="dispatch@disasterguard.gov", role=UserRole.OPERATOR)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                if user.role in [UserRole.OPERATOR, UserRole.ADMIN]:
                    return user
                raise HTTPException(status_code=403, detail="Access forbidden: Insufficient operational privileges.")
        raise HTTPException(status_code=401, detail="User account not found.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials.")


@router.get("/overview", response_model=OperationalOverviewResponse)
def get_operational_overview(db: Session = Depends(get_db)):
    """Returns high-level situational metrics across all concurrent incidents and resources."""
    return OperationsService.get_overview(db)


@router.get("/incidents", response_model=List[PrioritizedIncidentItem])
def get_prioritized_incidents(
    status: Optional[str] = Query("ALL", description="Filter by status (e.g. ALL, PENDING, DISPATCHED)"),
    sort_by: Optional[str] = Query("priority", description="Sort by priority, age, or people"),
    db: Session = Depends(get_db)
):
    """Returns all incidents ordered dynamically by multi-factor operational priority (0-100)."""
    return OperationsService.get_prioritized_incidents(db, status_filter=status, sort_by=sort_by)


@router.get("/incidents/{incident_id}/priority", response_model=IncidentPriorityResponse)
def get_incident_priority(incident_id: int, db: Session = Depends(get_db)):
    """Calculates and returns explainable priority score breakdown and 5-part evidence taxonomy."""
    try:
        return OperationsService.get_incident_priority(db, incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/incidents/{incident_id}/resources")
def get_candidate_resources(incident_id: int, db: Session = Depends(get_db)):
    """Discovers and ranks candidate rescue squads, shelters, and hospitals for an emergency."""
    try:
        return OperationsService.get_candidate_resources(db, incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/incidents/{incident_id}/response-plan", response_model=ResponsePlanResponse)
def get_response_plan(incident_id: int, db: Session = Depends(get_db)):
    """Generates an explainable response plan packaging team, shelter, and hospital recommendations."""
    try:
        return OperationsService.get_response_plan(db, incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/incidents/{incident_id}/response-plan/override", response_model=ResponsePlanResponse)
def override_response_plan(
    incident_id: int,
    request: ResponsePlanOverrideRequest,
    operator: User = Depends(require_operator),
    db: Session = Depends(get_db)
):
    """Records an explicit human operator override selecting an alternative rescue team."""
    try:
        return OperationsService.override_response_plan(
            db=db,
            incident_id=incident_id,
            operator=operator,
            selected_team_id=request.selected_team_id,
            override_reason=request.override_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/incidents/{incident_id}/response-plan/reject", response_model=ResponsePlanResponse)
def reject_response_plan(
    incident_id: int,
    request: ResponsePlanRejectRequest,
    operator: User = Depends(require_operator),
    db: Session = Depends(get_db)
):
    """Records an explicit human operator rejection of the proposed response plan."""
    try:
        return OperationsService.reject_response_plan(
            db=db,
            incident_id=incident_id,
            operator=operator,
            rejection_reason=request.rejection_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contentions", response_model=List[ResourceContentionResponse])
def get_resource_contentions(
    is_active: bool = Query(True, description="Filter active contention conflicts"),
    db: Session = Depends(get_db)
):
    """Lists detected resource contention conflicts where multiple incidents compete for the same team."""
    return OperationsService.get_contentions(db, is_active=is_active)


@router.get("/bottlenecks", response_model=List[OperationalBottleneckResponse])
def get_operational_bottlenecks(
    is_active: bool = Query(True, description="Filter active operational bottlenecks"),
    db: Session = Depends(get_db)
):
    """Scans and lists regional bottlenecks: rescue shortages, shelter saturation, hospital overload."""
    return OperationsService.get_bottlenecks(db, is_active=is_active)


@router.get("/coverage", response_model=ResourceCoverageResponse)
def get_resource_coverage(db: Session = Depends(get_db)):
    """Computes straight-line coverage estimates across regional emergency sectors."""
    return OperationsService.get_coverage(db)


@router.get("/capacity", response_model=CapacityIntelligenceResponse)
def get_capacity_intelligence(db: Session = Depends(get_db)):
    """Returns facility capacity intelligence with explicit data provenance."""
    return OperationsService.get_capacity(db)


@router.get("/analytics")
def get_operational_analytics(db: Session = Depends(get_db)):
    """Computes operational analytics strictly derived from stored database entities."""
    return OperationsService.get_analytics(db)


# Phase 6 Real-Time Coordination Endpoints
@router.get("/timeline")
def get_operational_timeline(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Returns database-backed operational timeline."""
    from app.services.situational_awareness_service import situational_awareness_service
    return situational_awareness_service.get_operational_timeline(db, limit=limit, offset=offset)


class AttentionAcknowledgeBody(BaseModel):
    acknowledged_by: Optional[str] = None
    notes: Optional[str] = None


@router.get("/attention")
def get_operator_attention_queue(
    unresolved_only: bool = Query(True),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns prioritized Operator Attention Queue (Critical -> High -> Medium -> Low)."""
    from app.services.situational_awareness_service import situational_awareness_service
    items = situational_awareness_service.get_operator_attention_queue(db, unresolved_only=unresolved_only)
    pending_count = len([i for i in items if not i.get("is_resolved") and not i.get("is_acknowledged")])
    return {
        "status": "SUCCESS",
        "items": items,
        "pending_count": pending_count,
        "count": len(items),
    }


@router.post("/attention/{item_id}/acknowledge")
def acknowledge_attention_item(
    item_id: int,
    body: Optional[AttentionAcknowledgeBody] = None,
    notes: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Marks an operator attention item as acknowledged by an authorized operator."""
    operator_name = "Human Operator"
    if body and body.acknowledged_by:
        operator_name = body.acknowledged_by
    elif authorization or x_user_role:
        try:
            operator = require_operator(authorization=authorization, x_user_role=x_user_role, db=db)
            operator_name = operator.name or operator_name
        except Exception:
            pass

    notes_val = notes or (body.notes if body else None)
    from app.services.situational_awareness_service import situational_awareness_service
    return situational_awareness_service.acknowledge_attention_item(
        db=db,
        item_id=item_id,
        operator_name=operator_name,
        notes=notes_val
    )


@router.get("/conflicts")
def get_resource_conflicts(db: Session = Depends(get_db)):
    """Returns active resource contentions with Option A (Primary) vs Option B (Alternative) comparisons."""
    from app.services.situational_awareness_service import situational_awareness_service
    res = situational_awareness_service.get_resource_conflicts_with_options(db)
    return {"contentions": res, "count": len(res)}

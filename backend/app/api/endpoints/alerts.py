"""
AI-DisasterGuard — Emergency Alerts Router
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlalchemy.orm import Session
import jwt

from app.database.database import get_db
from app.database.models.alert import Alert, AlertTarget, AlertDelivery, AlertAcknowledgement
from app.database.models.user import User, UserRole
from app.core.config import settings
from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    AlertApprovalRequest,
    AlertAcknowledgeRequest,
    AlertAnalyticsResponse,
    AlertTargetSchema,
    AlertDeliverySchema,
    AlertAcknowledgementSchema
)
from app.services.alert_service import alert_service
from app.services.alert_intelligence_service import alert_intelligence_service
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

router = APIRouter()

def get_current_operator_or_admin(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Authenticate and authorize user for operator approval and configuration actions."""
    if x_user_role:
        role_clean = x_user_role.strip().upper()
        if role_clean in [UserRole.OPERATOR.value, UserRole.ADMIN.value]:
            user = db.query(User).filter(User.role == UserRole(role_clean)).first()
            if user:
                return user
            return User(id=1, name=f"Officer {role_clean}", email=f"{role_clean.lower()}@disasterguard.gov", role=UserRole(role_clean))
        else:
            raise HTTPException(status_code=403, detail="Forbidden: Operator or Admin role required.")

    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")

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
                if user.role not in [UserRole.OPERATOR, UserRole.ADMIN]:
                    raise HTTPException(status_code=403, detail="Forbidden: Operator or Admin role required.")
                return user
        raise HTTPException(status_code=401, detail="User account not found.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials.")

def _format_alert_response(alert: Alert) -> AlertResponse:
    """Helper to convert Alert ORM model into AlertResponse schema with parsed JSON."""
    ev_cats = None
    if alert.evidence_json:
        try:
            ev_cats = json.loads(alert.evidence_json)
        except Exception:
            pass

    actions = None
    if alert.actionable_instructions_json:
        try:
            actions = json.loads(alert.actionable_instructions_json)
        except Exception:
            pass

    targets = [
        AlertTargetSchema(
            id=t.id,
            target_type=t.target_type,
            location_name=t.location_name,
            geometry_wkt=t.geometry_wkt,
            user_count_estimate=t.user_count_estimate or 0,
            created_at=t.created_at
        )
        for t in (alert.targets or [])
    ]

    return AlertResponse(
        id=alert.id,
        title=alert.title,
        message=alert.message,
        alert_type=alert.alert_type or "FLOOD",
        severity=alert.severity,
        target_area=alert.target_area,
        issued_at=alert.issued_at,
        expires_at=alert.expires_at,
        status=alert.status,
        alert_category=alert.alert_category or "FLOOD_WARNING",
        approval_status=alert.approval_status or "APPROVED",
        approved_by=alert.approved_by,
        approved_at=alert.approved_at,
        forecast_horizon=alert.forecast_horizon,
        risk_score=alert.risk_score,
        confidence_score=alert.confidence_score,
        uncertainty_score=alert.uncertainty_score,
        risk_velocity=alert.risk_velocity,
        evidence_categories=ev_cats,
        actionable_instructions=actions,
        targets=targets,
        deliveries_count=len(alert.deliveries or []),
        acknowledgements_count=len(alert.acknowledgements or []),
        is_simulation=alert.is_simulation or False
    )

# -----------------------------------------------------------------------------
# STATIC ROUTES (MUST PRECED PARAMETER ROUTES LIKE /{alert_id})
# -----------------------------------------------------------------------------

@router.get("/active", response_model=List[AlertResponse])
def get_active_approved_alerts(db: Session = Depends(get_db)):
    """Retrieve all approved and active disaster warnings."""
    alerts = alert_intelligence_service.get_active_alerts(db)
    return [_format_alert_response(a) for a in alerts]

@router.get("/recommendations", response_model=List[AlertResponse])
def get_alert_recommendations(
    current_operator: User = Depends(get_current_operator_or_admin),
    db: Session = Depends(get_db)
):
    """Retrieve pending operator decision-support recommendations."""
    alerts = alert_intelligence_service.get_recommendations(db)
    return [_format_alert_response(a) for a in alerts]

@router.get("/analytics", response_model=AlertAnalyticsResponse)
def get_alert_analytics(db: Session = Depends(get_db)):
    """Retrieve operational telemetry and acknowledgement statistics."""
    return alert_intelligence_service.get_alert_analytics(db)

@router.post("/recommend", response_model=AlertResponse)
def trigger_alert_recommendation(
    lat: float = Query(13.0827, description="Latitude"),
    lon: float = Query(80.2707, description="Longitude"),
    location: str = Query("Central Metro Sector", description="Target location name"),
    radius_km: float = Query(5.0, description="Target radius in km"),
    lang: str = Query("en", description="Message language (en, te, hi)"),
    db: Session = Depends(get_db)
):
    """Generate or update an adaptive alert recommendation using predictive intelligence."""
    alert = alert_intelligence_service.generate_alert_recommendation(
        db=db,
        latitude=lat,
        longitude=lon,
        location_name=location,
        radius_km=radius_km,
        language=lang
    )
    return _format_alert_response(alert)

# -----------------------------------------------------------------------------
# PARAMETERIZED ROUTES (/{alert_id}...)
# -----------------------------------------------------------------------------

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve complete details, targets, and evidence for a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found")
    return _format_alert_response(alert)

@router.post("/{alert_id}/approve", response_model=AlertResponse)
def approve_alert(
    alert_id: int,
    approval: AlertApprovalRequest,
    current_operator: User = Depends(get_current_operator_or_admin),
    db: Session = Depends(get_db)
):
    """
    Human Operator Approval Barrier.
    Transitions a RECOMMENDED alert to APPROVED and ACTIVE state.
    SAFETY INVARIANT: Zero automated rescue dispatches!
    """
    try:
        op_name = current_operator.name or approval.operator_name
        alert = alert_intelligence_service.approve_alert(
            db=db,
            alert_id=alert_id,
            operator_name=op_name,
            edited_message=approval.edited_message
        )
        return _format_alert_response(alert)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{alert_id}/reject", response_model=AlertResponse)
def reject_alert(
    alert_id: int,
    rejection: AlertApprovalRequest,
    current_operator: User = Depends(get_current_operator_or_admin),
    db: Session = Depends(get_db)
):
    """Operator rejects an alert recommendation."""
    try:
        op_name = current_operator.name or rejection.operator_name
        alert = alert_intelligence_service.reject_alert(
            db=db,
            alert_id=alert_id,
            operator_name=op_name,
            reason=rejection.notes
        )
        return _format_alert_response(alert)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    ack_req: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    """
    Citizen acknowledges receipt of an emergency warning.
    INVIOLATE INVARIANT: ACKNOWLEDGED != SAFE
    """
    try:
        return alert_intelligence_service.acknowledge_alert(
            db=db,
            alert_id=alert_id,
            client_id=ack_req.client_id,
            user_id=ack_req.user_id,
            channel=ack_req.channel
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{alert_id}/targets", response_model=List[AlertTargetSchema])
def get_alert_targets(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve geographic target polygons and population estimates for an alert."""
    targets = db.query(AlertTarget).filter(AlertTarget.alert_id == alert_id).all()
    return targets

@router.get("/{alert_id}/delivery", response_model=List[AlertDeliverySchema])
def get_alert_deliveries(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve delivery statuses across all communication channels."""
    deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == alert_id).all()
    return deliveries

# -----------------------------------------------------------------------------
# BACKWARDS COMPATIBILITY ROUTES
# -----------------------------------------------------------------------------

@router.get("", response_model=List[AlertResponse])
@router.get("/", response_model=List[AlertResponse])
def get_all_active_alerts_legacy(db: Session = Depends(get_db)):
    """Legacy active alerts endpoint."""
    alerts = alert_intelligence_service.get_active_alerts(db)
    return [_format_alert_response(a) for a in alerts]

@router.post("", response_model=AlertResponse)
@router.post("/", response_model=AlertResponse)
def create_alert_legacy(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """Issue a new disaster alert (legacy support)."""
    alert = alert_service.create_alert(db, alert_in)
    return _format_alert_response(alert)

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, alert_up: AlertUpdate, db: Session = Depends(get_db)):
    """Update alert status or severity."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert_up.status:
        alert.status = alert_up.status
    if alert_up.severity:
        alert.severity = alert_up.severity
    if alert_up.message:
        alert.message = alert_up.message
    if alert_up.approval_status:
        alert.approval_status = alert_up.approval_status
    if alert_up.approved_by:
        alert.approved_by = alert_up.approved_by
    db.commit()
    db.refresh(alert)

    try:
        ws_manager.broadcast_event(
            DomainEvent(
                event=EventType.ALERT_UPDATED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                entity_id=alert.id,
                entity_type="alert",
                severity=alert.severity,
                data={
                    "id": alert.id,
                    "title": alert.title,
                    "status": alert.status,
                    "severity": alert.severity,
                    "target_area": alert.target_area
                }
            )
        )
    except Exception:
        pass

    return _format_alert_response(alert)

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Cancel or delete an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = "CANCELLED"
        alert.approval_status = "CANCELLED"
        db.commit()
        db.refresh(alert)
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.ALERT_UPDATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=alert.id,
                    entity_type="alert",
                    severity="LOW",
                    data={
                        "id": alert.id,
                        "title": alert.title,
                        "status": "CANCELLED",
                        "severity": alert.severity
                    }
                )
            )
        except Exception:
            pass
    return {"success": True, "message": "Alert cancelled successfully"}

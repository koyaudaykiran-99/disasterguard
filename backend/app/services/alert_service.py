from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database.models.alert import Alert
from app.schemas.alert import AlertCreate
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

class AlertService:
    @staticmethod
    def get_active_alerts(db: Session) -> List[Alert]:
        return db.query(Alert).filter(Alert.status == "ACTIVE").all()

    @staticmethod
    def create_alert(db: Session, alert_in: AlertCreate) -> Alert:
        expires_at = None
        if alert_in.expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=alert_in.expires_in_hours)
            
        alert = Alert(
            title=alert_in.title,
            message=alert_in.message,
            alert_type=alert_in.alert_type,
            severity=alert_in.severity,
            target_area=alert_in.target_area,
            issued_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            status="ACTIVE"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Broadcast ALERT_CREATED
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.ALERT_CREATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=alert.id,
                    entity_type="alert",
                    severity=alert.severity,
                    data={
                        "id": alert.id,
                        "title": alert.title,
                        "message": alert.message,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "target_area": alert.target_area,
                        "status": alert.status,
                        "issued_at": alert.issued_at.isoformat() if alert.issued_at else None,
                        "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
                    }
                )
            )
        except Exception as e:
            pass

        return alert

    @staticmethod
    def auto_generate_threshold_alert(db: Session, risk_score: int, location: str = "Central Metro Sector 4") -> Optional[Alert]:
        """Automatically generate alerts when risk thresholds are crossed."""
        if risk_score >= 76:
            return AlertService.create_alert(
                db,
                AlertCreate(
                    title="CRITICAL FLOOD EVACUATION ADVISORY",
                    message=f"Risk Score escalated to {risk_score}/100. Emergency command mandates immediate high-ground evacuation.",
                    alert_type="FLOOD",
                    severity="CRITICAL",
                    target_area=location,
                    expires_in_hours=6
                )
            )
        elif risk_score >= 51:
            return AlertService.create_alert(
                db,
                AlertCreate(
                    title="HIGH FLOOD RISK WARNING",
                    message=f"Risk Score escalated to {risk_score}/100. Prepare emergency survival kits.",
                    alert_type="FLOOD",
                    severity="HIGH",
                    target_area=location,
                    expires_in_hours=12
                )
            )
        return None

alert_service = AlertService()

"""
AI-DisasterGuard — Alert Intelligence Service
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.alert import Alert, AlertTarget, AlertDelivery, AlertAcknowledgement
from app.database.models.rescue import RescueAssignment
from app.schemas.events import DomainEvent, EventType
from app.services.websocket_manager import ws_manager
from app.core.logging import logger

import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.alerts.alert_engine import alert_engine
from ml.alerts import AlertCategory, AlertSeverity, ApprovalStatus, DeliveryChannel, DeliveryStatus
from ml.forecasting.forecast_engine import ForecastEngine
from app.services.geospatial.spatial_service import spatial_service

class AlertIntelligenceService:
    """
    Central orchestration service for adaptive warning generation, geospatial targeting,
    operator approval barrier, delivery lifecycle, and citizen acknowledgement tracking.
    """

    def generate_alert_recommendation(
        self,
        db: Session,
        latitude: float = 13.0827,
        longitude: float = 80.2707,
        location_name: str = "Central Metro Sector",
        radius_km: float = 5.0,
        language: str = "en",
        is_simulation: bool = False
    ) -> Alert:
        """
        Ingest multi-horizon forecasting + flood intelligence to evaluate risk
        and generate or update an alert.
        """
        # Ingest multi-horizon forecast from ForecastEngine
        forecast_packet = ForecastEngine.compute_forecast(latitude=latitude, longitude=longitude)
        horizons_data = forecast_packet.get("horizons", {})
        trajectory_data = forecast_packet.get("trajectory", {})
        current_risk = forecast_packet.get("current", {}).get("risk_score", 50)
        uncertainty_score = forecast_packet.get("uncertainty_overview", {}).get("average_uncertainty", 0.20)
        confidence_score = forecast_packet.get("uncertainty_overview", {}).get("average_confidence", 0.80)

        # Ingest spatial flood susceptibility
        spatial_intel = spatial_service.calculate_flood_intelligence(latitude, longitude, db=db)
        susceptibility_score = spatial_intel.get("susceptibility_score", 50)

        # Retrieve active alerts for deduplication
        active_alerts = db.query(Alert).filter(Alert.status.in_(["ACTIVE", "RECOMMENDED"])).all()

        # Execute ML AlertEngine
        packet = alert_engine.generate_alert_packet(
            current_risk=current_risk,
            horizons_data=horizons_data,
            trajectory_data=trajectory_data,
            susceptibility_score=susceptibility_score,
            uncertainty_score=uncertainty_score,
            confidence_score=confidence_score,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            radius_km=radius_km,
            active_alerts=active_alerts,
            language=language,
            db_session=db
        )

        dedup_info = packet.get("deduplication", {})

        # Handle deduplication update if duplicate alert was identified
        if dedup_info.get("is_duplicate") and dedup_info.get("existing_alert_id"):
            existing = db.query(Alert).filter(Alert.id == dedup_info["existing_alert_id"]).first()
            if existing:
                # Update telemetry
                existing.risk_score = packet["peak_risk"]
                existing.confidence_score = packet["confidence_score"]
                existing.uncertainty_score = packet["uncertainty_score"]
                existing.risk_velocity = packet["risk_velocity"]
                existing.message = packet["message"]
                existing.evidence_json = json.dumps(packet["evidence_categories"])
                existing.actionable_instructions_json = json.dumps(packet["actionable_instructions"])
                
                # Check for escalation
                from ml.alerts.escalation import EscalationEngine
                transition = EscalationEngine.evaluate_transition(
                    current_severity=existing.severity,
                    target_severity=packet["severity"],
                    risk_score_delta=(packet["peak_risk"] - (existing.risk_score or packet["peak_risk"]))
                )
                if transition["is_transition"]:
                    existing.severity = transition["effective_severity"]
                    event_type = EventType.ALERT_ESCALATED if transition["action"] == "ESCALATE" else EventType.ALERT_DEESCALATED
                    db.commit()
                    db.refresh(existing)
                    self._broadcast_alert_event(existing, event_type)
                    return existing

                db.commit()
                db.refresh(existing)
                self._broadcast_alert_event(existing, EventType.ALERT_UPDATED)
                return existing

        # Create new Alert
        approval_status = packet["approval_status"]
        status = "ACTIVE" if approval_status == ApprovalStatus.APPROVED.value else "RECOMMENDED"

        alert = Alert(
            title=packet["headline"][:180],
            message=packet["message"],
            alert_type="FLOOD",
            alert_category=packet["category"],
            severity=packet["severity"],
            target_area=location_name,
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
            status=status,
            approval_status=approval_status,
            forecast_horizon=packet["peak_horizon"],
            risk_score=packet["peak_risk"],
            confidence_score=packet["confidence_score"],
            uncertainty_score=packet["uncertainty_score"],
            risk_velocity=packet["risk_velocity"],
            evidence_json=json.dumps(packet["evidence_categories"]),
            actionable_instructions_json=json.dumps(packet["actionable_instructions"]),
            is_simulation=is_simulation
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Create AlertTarget
        tgt_data = packet["targeting"]
        target = AlertTarget(
            alert_id=alert.id,
            target_type=tgt_data["target_type"],
            location_name=location_name,
            geometry_wkt=tgt_data["geometry_wkt"],
            user_count_estimate=tgt_data["estimated_users"],
            created_at=datetime.now(timezone.utc)
        )
        db.add(target)
        db.commit()
        db.refresh(target)

        # Create initial AlertDeliveries
        channels = [
            (DeliveryChannel.IN_APP.value, DeliveryStatus.DELIVERED.value if status == "ACTIVE" else DeliveryStatus.PENDING.value),
            (DeliveryChannel.WEBSOCKET.value, DeliveryStatus.DELIVERED.value if status == "ACTIVE" else DeliveryStatus.PENDING.value),
            (DeliveryChannel.SMS_READY.value, DeliveryStatus.PENDING.value),
            (DeliveryChannel.RELAY_GATEWAY.value, DeliveryStatus.PENDING.value)
        ]
        for ch, st in channels:
            delivery = AlertDelivery(
                alert_id=alert.id,
                target_id=target.id,
                channel=ch,
                status=st,
                attempt_count=1,
                sent_at=datetime.now(timezone.utc),
                delivered_at=datetime.now(timezone.utc) if st == DeliveryStatus.DELIVERED.value else None
            )
            db.add(delivery)
        db.commit()

        # Broadcast event
        event_type = EventType.ALERT_RECOMMENDATION_CREATED if approval_status == ApprovalStatus.RECOMMENDED.value else EventType.ALERT_CREATED
        self._broadcast_alert_event(alert, event_type)

        # STRICT SAFETY BARRIER VERIFICATION: Zero dispatch created!
        logger.info(f"ALERT_INTELLIGENCE: Generated Alert #{alert.id} ({alert.alert_category}, {alert.severity}, {alert.approval_status})")
        return alert

    def get_active_alerts(self, db: Session) -> List[Alert]:
        """Fetch all approved, currently active alerts."""
        return db.query(Alert).filter(
            Alert.status == "ACTIVE",
            Alert.approval_status == ApprovalStatus.APPROVED.value
        ).order_by(desc(Alert.issued_at)).all()

    def get_recommendations(self, db: Session) -> List[Alert]:
        """Fetch all pending operator recommendations."""
        return db.query(Alert).filter(
            Alert.approval_status == ApprovalStatus.RECOMMENDED.value
        ).order_by(desc(Alert.issued_at)).all()

    def approve_alert(
        self,
        db: Session,
        alert_id: int,
        operator_name: str = "Authorized Operator",
        edited_message: Optional[str] = None
    ) -> Alert:
        """
        Explicit Operator Approval Barrier.
        Transitions RECOMMENDED alert to APPROVED and ACTIVE.
        SAFETY RULE: NEVER creates a RescueAssignment!
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert #{alert_id} not found")

        alert.approval_status = ApprovalStatus.APPROVED.value
        alert.status = "ACTIVE"
        alert.approved_by = operator_name
        alert.approved_at = datetime.now(timezone.utc)
        if edited_message:
            alert.message = edited_message

        # Update deliveries to DELIVERED for active channels
        deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == alert.id).all()
        for d in deliveries:
            if d.channel in [DeliveryChannel.IN_APP.value, DeliveryChannel.WEBSOCKET.value]:
                d.status = DeliveryStatus.DELIVERED.value
                d.delivered_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(alert)

        # Broadcast approval and activation
        self._broadcast_alert_event(alert, EventType.ALERT_APPROVED)
        self._broadcast_alert_event(alert, EventType.ALERT_CREATED)

        logger.info(f"ALERT_APPROVED: Operator '{operator_name}' approved Alert #{alert.id} ({alert.alert_category})")
        return alert

    def reject_alert(
        self,
        db: Session,
        alert_id: int,
        operator_name: str = "Authorized Operator",
        reason: Optional[str] = None
    ) -> Alert:
        """
        Operator rejects an alert recommendation.
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert #{alert_id} not found")

        alert.approval_status = ApprovalStatus.REJECTED.value
        alert.status = "CANCELLED"
        alert.approved_by = operator_name
        alert.approved_at = datetime.now(timezone.utc)

        deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == alert.id).all()
        for d in deliveries:
            d.status = DeliveryStatus.FAILED.value
            d.failed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(alert)

        self._broadcast_alert_event(alert, EventType.ALERT_REJECTED)
        logger.info(f"ALERT_REJECTED: Operator '{operator_name}' rejected Alert #{alert.id}. Reason: {reason}")
        return alert

    def acknowledge_alert(
        self,
        db: Session,
        alert_id: int,
        client_id: Optional[str] = None,
        user_id: Optional[int] = None,
        channel: str = DeliveryChannel.IN_APP.value
    ) -> Dict[str, Any]:
        """
        Record citizen receipt acknowledgement.
        INVIOLATE INVARIANT: ACKNOWLEDGED != SAFE
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert #{alert_id} not found")

        ack = AlertAcknowledgement(
            alert_id=alert.id,
            user_id=user_id,
            client_id=client_id,
            channel=channel,
            acknowledged_at=datetime.now(timezone.utc)
        )
        db.add(ack)
        db.commit()
        db.refresh(ack)

        # Broadcast event
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.ALERT_ACKNOWLEDGED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=alert.id,
                    entity_type="alert",
                    severity=alert.severity,
                    data={
                        "ack_id": ack.id,
                        "alert_id": alert.id,
                        "client_id": client_id,
                        "acknowledged_at": ack.acknowledged_at.isoformat()
                    }
                )
            )
        except Exception:
            pass

        return {
            "success": True,
            "ack_id": ack.id,
            "alert_id": alert.id,
            "acknowledged_at": ack.acknowledged_at.isoformat(),
            "safety_invariant": {
                "acknowledged_implies_safe": False,
                "sos_priority_unaffected": True,
                "sos_suppressed": False,
                "notice": "Receipt acknowledged. This does not verify physical safety. If in immediate danger, use SOS."
            }
        }

    def get_alert_analytics(self, db: Session) -> Dict[str, Any]:
        """
        Compute real-time operational alert metrics for the Command Centre.
        """
        active_count = db.query(Alert).filter(Alert.status == "ACTIVE", Alert.approval_status == ApprovalStatus.APPROVED.value).count()
        rec_count = db.query(Alert).filter(Alert.approval_status == ApprovalStatus.RECOMMENDED.value).count()
        crit_count = db.query(Alert).filter(Alert.status == "ACTIVE", Alert.severity == AlertSeverity.CRITICAL.value).count()
        warn_count = db.query(Alert).filter(Alert.status == "ACTIVE", Alert.severity == AlertSeverity.WARNING.value).count()

        total_users_est = 0
        targets = db.query(AlertTarget).all()
        for t in targets:
            total_users_est += (t.user_count_estimate or 0)

        total_acks = db.query(AlertAcknowledgement).count()
        total_deliveries = db.query(AlertDelivery).count()
        delivered_count = db.query(AlertDelivery).filter(AlertDelivery.status == DeliveryStatus.DELIVERED.value).count()

        ack_rate = (total_acks / max(1, total_users_est)) * 100 if total_users_est > 0 else 0.0
        del_rate = (delivered_count / max(1, total_deliveries)) * 100 if total_deliveries > 0 else 100.0

        return {
            "active_alerts_count": active_count,
            "recommendations_count": rec_count,
            "critical_alerts_count": crit_count,
            "warning_alerts_count": warn_count,
            "total_affected_users_estimate": total_users_est,
            "total_acknowledgements": total_acks,
            "acknowledgement_rate_percent": round(ack_rate, 1),
            "delivery_success_rate_percent": round(del_rate, 1),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _broadcast_alert_event(self, alert: Alert, event_type: EventType):
        """Emit WebSocket notification after database transaction commits."""
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=event_type,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=alert.id,
                    entity_type="alert",
                    severity=alert.severity,
                    data={
                        "id": alert.id,
                        "title": alert.title,
                        "category": alert.alert_category,
                        "severity": alert.severity,
                        "approval_status": alert.approval_status,
                        "status": alert.status,
                        "target_area": alert.target_area,
                        "forecast_horizon": alert.forecast_horizon,
                        "risk_score": alert.risk_score,
                        "confidence_score": alert.confidence_score,
                        "issued_at": alert.issued_at.isoformat() if alert.issued_at else None
                    }
                )
            )
        except Exception:
            pass

alert_intelligence_service = AlertIntelligenceService()

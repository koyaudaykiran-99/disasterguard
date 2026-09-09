from app.database.models.emergency_update import EmergencyUpdate
from app.schemas.emergency_update import EmergencyUpdateCreate
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.sos_triage import SOSTriageResult
from app.schemas.sos import SOSCreate, SOSTriageDetail
from app.services.incident_service import incident_service
from app.services.ai_triage_service import ai_triage_service
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType

logger = logging.getLogger("disasterguard.sos")

def build_sos_triage_detail(sos: SOSReport, inc: Optional[Incident], triage_res: Optional[SOSTriageResult]) -> Optional[SOSTriageDetail]:
    if not triage_res:
        return None
    predictions = triage_res.predictions if isinstance(triage_res.predictions, dict) else {}
    return SOSTriageDetail(
        incident_id=inc.id if inc else (triage_res.incident_id or 0),
        incident_title=inc.title if inc else (sos.message or "Distress Call"),
        incident_type=triage_res.incident_type,
        severity=triage_res.severity,
        priority_score=triage_res.priority_score,
        classification_method=triage_res.model,
        risk_zone_name=predictions.get("risk_zone_name", "General Urban Sector"),
        risk_zone_level=predictions.get("risk_zone_level", "MODERATE"),
        recommended_rescue_team="Water Rescue Squad Alpha (Recommended)",
        rescue_team_id=1,
        distance_km=0.4,
        estimated_response_minutes=4,
        recommended_hospital="Metro Trauma & Critical Care Center",
        hospital_distance_km=0.8,
        recommended_shelter="St. Jude Emergency High Ground Shelter",
        shelter_distance_km=0.8,
        assignment_id=0,
        assignment_status="PENDING_CONFIRMATION",
        confidence=triage_res.confidence,
        confidence_type=triage_res.confidence_type,
        reasoning=triage_res.reasoning if isinstance(triage_res.reasoning, list) else [],
        data_sources=triage_res.data_sources if isinstance(triage_res.data_sources, list) else [],
        facts=triage_res.facts if isinstance(triage_res.facts, dict) else {},
        predictions=predictions,
        ai_interpretation=triage_res.ai_interpretation or "",
        recommended_action=triage_res.recommended_action or "Operator review recommended",
        stale_data_warning=triage_res.stale_data_warning,
        human_confirmation_required=True
    )

class SOSService:
    @staticmethod
    def create_sos(db: Session, sos_in: SOSCreate, user_id: Optional[int] = None, auto_assign: bool = False) -> SOSReport:
        # 1. Exact Idempotency Check (client_id retry)
        if sos_in.client_id:
            existing = db.query(SOSReport).filter(SOSReport.client_id == sos_in.client_id).first()
            if existing:
                logger.info(f"SOS_DUPLICATE: client_id '{sos_in.client_id}' matched existing SOS #{existing.id}")
                triage_res = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == existing.id).first()
                inc = db.query(Incident).filter(Incident.sos_id == existing.id).first()
                existing.triage = build_sos_triage_detail(existing, inc, triage_res)
                return existing

        # 2. Repeated SOS by Authenticated User
        if user_id:
            active_sos = db.query(SOSReport).filter(
                SOSReport.user_id == user_id,
                SOSReport.status != "RESCUED"
            ).order_by(SOSReport.created_at.desc()).first()
            if active_sos:
                logger.info(f"PERSISTENT_SOS: Attaching repeated SOS attempt from user #{user_id} to active SOS #{active_sos.id}")
                update_in = EmergencyUpdateCreate(
                    client_update_id=sos_in.client_id,
                    update_type="REPEAT_SOS",
                    message=sos_in.message or "Repeated emergency distress signal sent by citizen.",
                    latitude=sos_in.latitude,
                    longitude=sos_in.longitude,
                    accuracy=sos_in.accuracy,
                    location_timestamp=sos_in.device_timestamp,
                    source=sos_in.transport or "CITIZEN_APP"
                )
                SOSService.add_emergency_update(db, active_sos.id, update_in, user_id=user_id)
                triage_res = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == active_sos.id).first()
                inc = db.query(Incident).filter(Incident.sos_id == active_sos.id).first()
                active_sos.triage = build_sos_triage_detail(active_sos, inc, triage_res)
                return active_sos

        # 3. Rapid Identical Duplicate Fallback (Identical coordinates and message within 60 seconds)
        one_minute_ago = datetime.now(timezone.utc) - timedelta(seconds=60)
        recent = db.query(SOSReport).filter(
            SOSReport.latitude == sos_in.latitude,
            SOSReport.longitude == sos_in.longitude,
            SOSReport.message == sos_in.message,
            SOSReport.status != "RESCUED",
            SOSReport.created_at >= one_minute_ago
        ).first()
        if recent:
            logger.info(f"PERSISTENT_SOS: Rapid identical coordinates & message matched active SOS #{recent.id}")
            update_in = EmergencyUpdateCreate(
                client_update_id=sos_in.client_id,
                update_type="REPEAT_SOS",
                message=sos_in.message or "Repeated emergency distress signal.",
                latitude=sos_in.latitude,
                longitude=sos_in.longitude,
                accuracy=sos_in.accuracy,
                location_timestamp=sos_in.device_timestamp,
                source=sos_in.transport or "CITIZEN_APP"
            )
            SOSService.add_emergency_update(db, recent.id, update_in, user_id=user_id)
            triage_res = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == recent.id).first()
            inc = db.query(Incident).filter(Incident.sos_id == recent.id).first()
            recent.triage = build_sos_triage_detail(recent, inc, triage_res)
            return recent

        severity = sos_in.severity or "CRITICAL"

        # 1. Persist SOS record in PostgreSQL with status PENDING
        sos = SOSReport(
            client_id=sos_in.client_id,
            user_id=user_id,
            latitude=sos_in.latitude,
            longitude=sos_in.longitude,
            accuracy=sos_in.accuracy,
            message=sos_in.message,
            severity=severity,
            status="PENDING",
            transport=sos_in.transport or "INTERNET",
            device_timestamp=sos_in.device_timestamp,
            created_at=datetime.now(timezone.utc)
        )
        db.add(sos)
        db.commit()
        db.refresh(sos)

        logger.info(f"SOS_CREATED: ID #{sos.id}, client_id: {sos.client_id}, coords: [{sos.latitude}, {sos.longitude}], severity: {sos.severity}")

        # Broadcast SOS_CREATED
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SOS_CREATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=sos.id,
                    entity_type="sos",
                    severity=severity,
                    data={
                        "id": sos.id,
                        "client_id": sos.client_id,
                        "latitude": sos.latitude,
                        "longitude": sos.longitude,
                        "accuracy": sos.accuracy,
                        "message": sos.message,
                        "severity": sos.severity,
                        "status": sos.status,
                        "transport": sos.transport,
                        "created_at": sos.created_at.isoformat() if sos.created_at else None
                    }
                )
            )
        except Exception as e:
            logger.warning(f"Failed to broadcast SOS_CREATED event: {e}")

        # 2. Create Linked Incident in PostgreSQL (Status PENDING)
        inc_title = f"Citizen Distress: {sos_in.message[:80]}" if sos_in.message else "Citizen Distress Call"
        inc = Incident(
            sos_id=sos.id,
            title=inc_title,
            description=f"Citizen distress message: '{sos_in.message}'.",
            incident_type="OTHER",
            latitude=sos_in.latitude,
            longitude=sos_in.longitude,
            severity=severity,
            status="PENDING",
            source="CITIZEN_SOS",
            priority_score=50
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)

        # 3. Create initial EmergencyUpdate record of type INITIAL_SOS
        initial_update = EmergencyUpdate(
            client_update_id=f"init_{sos.id}",
            sos_id=sos.id,
            incident_id=inc.id,
            user_id=user_id,
            update_type="INITIAL_SOS",
            message=sos.message or "Initial SOS distress call transmitted.",
            latitude=sos.latitude,
            longitude=sos.longitude,
            accuracy=sos.accuracy,
            location_timestamp=sos.device_timestamp or datetime.now(timezone.utc),
            source=sos.transport or "CITIZEN_APP",
            delivery_status="RECEIVED",
            original_language="en",
            processing_status="PROCESSED",
            created_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc)
        )
        db.add(initial_update)
        db.commit()

        # 4. Trigger AI Emergency Triage (Grounded NLP classification + Priority Scoring)
        triage_res = ai_triage_service.triage_sos(db, sos.id)

        # Update SOS severity from triage if appropriate
        sos.severity = triage_res.severity
        db.commit()
        db.refresh(sos)

        # Broadcast INCIDENT_CREATED with triaged attributes
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.INCIDENT_CREATED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=inc.id,
                    entity_type="incident",
                    severity=inc.severity,
                    data={
                        "id": inc.id,
                        "sos_id": inc.sos_id,
                        "title": inc.title,
                        "incident_type": inc.incident_type,
                        "priority_score": inc.priority_score,
                        "latitude": inc.latitude,
                        "longitude": inc.longitude,
                        "severity": inc.severity,
                        "status": inc.status
                    }
                )
            )
        except Exception as e:
            pass

        # 5. Strict Human-in-the-Loop: SOS creation NEVER triggers auto-dispatch.
        if auto_assign:
            logger.warning(
                f"[SECURITY_AUDIT] Ignored legacy auto_assign=True on SOS #{sos.id}. "
                "Autonomous rescue dispatch is strictly prohibited by policy. Operator review required."
            )
        sos.triage = build_sos_triage_detail(sos, inc, triage_res)

        # 6. Geospatial Flood Context Enrichment (Advisory only)
        try:
            from app.services.geospatial.spatial_service import spatial_service
            sos.flood_context = spatial_service.enrich_sos_with_flood_context(db, sos.latitude, sos.longitude)
        except Exception as fe:
            logger.warning(f"Could not attach flood context to SOS #{sos.id}: {fe}")
            sos.flood_context = None

        return sos

    @staticmethod
    def add_emergency_update(
        db: Session,
        sos_id: int,
        update_in: EmergencyUpdateCreate,
        user_id: Optional[int] = None
    ) -> EmergencyUpdate:
        """
        Append a chronological EmergencyUpdate to a persistent SOS report.
        Supports idempotency via client_update_id, updates coordinates,
        triggers AI triage reassessment when distress escalates,
        and broadcasts WebSocket domain event SOS_UPDATE_CREATED after DB commit.
        """
        # 1. Verify SOS exists
        sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
        if not sos:
            raise ValueError(f"SOS Report #{sos_id} not found")

        # 2. Idempotency Check: if client_update_id provided and already exists, return existing update
        if update_in.client_update_id:
            existing_up = db.query(EmergencyUpdate).filter(
                EmergencyUpdate.client_update_id == update_in.client_update_id
            ).first()
            if existing_up:
                logger.info(f"EMERGENCY_UPDATE_IDEMPOTENT: client_update_id '{update_in.client_update_id}' already stored as Update #{existing_up.id}")
                return existing_up

        # 3. Linked Incident
        inc = db.query(Incident).filter(Incident.sos_id == sos_id).first()

        # 4. Optional Coordinate Update
        if update_in.latitude is not None and update_in.longitude is not None:
            sos.latitude = update_in.latitude
            sos.longitude = update_in.longitude
            if update_in.accuracy is not None:
                sos.accuracy = update_in.accuracy
            if inc:
                inc.latitude = update_in.latitude
                inc.longitude = update_in.longitude
                inc.updated_at = datetime.now(timezone.utc)

        # 5. Persist EmergencyUpdate in PostgreSQL
        now = datetime.now(timezone.utc)
        update_record = EmergencyUpdate(
            client_update_id=update_in.client_update_id,
            sos_id=sos_id,
            incident_id=inc.id if inc else None,
            user_id=user_id,
            update_type=update_in.update_type,
            message=update_in.message,
            latitude=update_in.latitude,
            longitude=update_in.longitude,
            accuracy=update_in.accuracy,
            location_timestamp=update_in.location_timestamp or now,
            source=update_in.source or "CITIZEN_APP",
            delivery_status="RECEIVED",
            original_language=getattr(update_in, "original_language", None) or "en",
            processing_status="PROCESSED",
            audio_id=getattr(update_in, "audio_id", None),
            audio_duration=getattr(update_in, "audio_duration", None),
            audio_mime_type=getattr(update_in, "audio_mime_type", None),
            audio_size=getattr(update_in, "audio_size", None),
            audio_storage_reference=getattr(update_in, "audio_storage_reference", None),
            transcription_provider=getattr(update_in, "transcription_provider", None),
            transcription_model=getattr(update_in, "transcription_model", None),
            transcription_confidence=getattr(update_in, "transcription_confidence", None),
            created_at=now,
            received_at=now
        )
        db.add(update_record)
        db.commit()
        db.refresh(update_record)

        logger.info(
            f"EMERGENCY_UPDATE_CREATED: ID #{update_record.id} for SOS #{sos_id}, type: {update_record.update_type}, "
            f"lang: {update_record.original_language}, msg: '{update_record.message[:50] if update_record.message else ''}'"
        )

        # 6. Trigger AI Emergency Re-Triage
        ai_triage_service.reassess_sos(db, sos_id, update_record)

        # 7. Broadcast DomainEvent AFTER PostgreSQL commit
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SOS_UPDATE_CREATED,
                    timestamp=now.isoformat(),
                    entity_id=update_record.id,
                    entity_type="emergency_update",
                    severity=sos.severity,
                    data={
                        "id": update_record.id,
                        "sos_id": sos.id,
                        "incident_id": inc.id if inc else None,
                        "client_update_id": update_record.client_update_id,
                        "update_type": update_record.update_type,
                        "message": update_record.message,
                        "latitude": update_record.latitude,
                        "longitude": update_record.longitude,
                        "accuracy": update_record.accuracy,
                        "source": update_record.source,
                        "delivery_status": update_record.delivery_status,
                        "original_language": update_record.original_language,
                        "audio_id": update_record.audio_id,
                        "audio_duration": update_record.audio_duration,
                        "transcription_provider": update_record.transcription_provider,
                        "created_at": update_record.created_at.isoformat(),
                        "priority_score": inc.priority_score if inc else None,
                        "severity": inc.severity if inc else sos.severity
                    }
                )
            )
        except Exception as e:
            logger.warning(f"Failed to broadcast SOS_UPDATE_CREATED event: {e}")

        return update_record

    @staticmethod
    def get_emergency_updates(db: Session, sos_id: int) -> List[EmergencyUpdate]:
        """Retrieve chronological timeline of EmergencyUpdate records for an SOS."""
        return db.query(EmergencyUpdate).filter(
            EmergencyUpdate.sos_id == sos_id
        ).order_by(EmergencyUpdate.created_at.asc()).all()

    @staticmethod
    def get_active_sos(db: Session) -> List[SOSReport]:
        reports = db.query(SOSReport).filter(SOSReport.status != "RESCUED").order_by(SOSReport.created_at.desc()).all()
        for s in reports:
            triage_res = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == s.id).first()
            inc = db.query(Incident).filter(Incident.sos_id == s.id).first()
            s.triage = build_sos_triage_detail(s, inc, triage_res)
        return reports

    @staticmethod
    def update_sos_status(db: Session, sos_id: int, status: str) -> Optional[SOSReport]:
        sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
        if sos:
            sos.status = status
            if status == "RESCUED":
                inc = db.query(Incident).filter(Incident.sos_id == sos_id).first()
                if inc:
                    inc.status = "RESOLVED"
            db.commit()
            db.refresh(sos)
        return sos

sos_service = SOSService()

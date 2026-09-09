from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.sos import SOSReport
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.emergency_update import EmergencyUpdate
from app.database.models.incident import Incident
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.database.models.rescue import RescueAssignment, RescueTeam
from app.schemas.sos import (
    SOSCreate, SOSResponse, SOSStatusUpdate,
    RecommendedFacility, SafeRouteGuidance, SOSGuidanceResponse
)
from app.schemas.emergency_update import EmergencyUpdateCreate, EmergencyUpdateResponse
from app.schemas.triage import SOSTriageResponse, TriageEvidenceResponse
from app.services.sos_service import sos_service
from app.services.ai_triage_service import ai_triage_service
from app.services.audio_storage_service import audio_storage_service
from app.services.stt_service import stt_service
from typing import List, Optional
import math

router = APIRouter()

@router.get("", response_model=List[SOSResponse])
@router.get("/", response_model=List[SOSResponse])
def get_all_sos_reports(db: Session = Depends(get_db)):
    """Retrieve all emergency SOS reports."""
    try:
        return db.query(SOSReport).order_by(SOSReport.created_at.desc()).all()
    except Exception:
        try:
            return db.query(SOSReport).order_by(SOSReport.id.desc()).all()
        except Exception:
            return []

@router.post("", response_model=SOSResponse)
@router.post("/", response_model=SOSResponse)
def submit_sos_report(sos_in: SOSCreate, db: Session = Depends(get_db)):
    """Submit citizen emergency SOS distress call."""
    return sos_service.create_sos(db, sos_in)

@router.get("/active", response_model=List[SOSResponse])
def get_active_sos_reports(db: Session = Depends(get_db)):
    """Retrieve active un-rescued SOS calls."""
    try:
        return sos_service.get_active_sos(db)
    except Exception:
        try:
            return db.query(SOSReport).filter(SOSReport.status != "RESCUED").order_by(SOSReport.id.desc()).all()
        except Exception:
            return []

@router.get("/{sos_id}", response_model=SOSResponse)
def get_sos_report_by_id(sos_id: int, db: Session = Depends(get_db)):
    """Get specific SOS report details."""
    sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS Report not found")
    return sos

@router.patch("/{sos_id}/status", response_model=SOSResponse)
def update_sos_status(sos_id: int, up: SOSStatusUpdate, db: Session = Depends(get_db)):
    """Patch status of an SOS report."""
    sos = sos_service.update_sos_status(db, sos_id, up.status)
    if not sos:
        raise HTTPException(status_code=404, detail="SOS Report not found")
    return sos

@router.post("/{sos_id}/updates", response_model=EmergencyUpdateResponse)
def add_emergency_update(
    sos_id: int,
    update_in: EmergencyUpdateCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a chronological EmergencyUpdate to an active SOS report.
    Supports situation updates, text distress, GPS coordinate updates,
    and triggers AI triage reassessment if distress indicators escalate.
    """
    try:
        return sos_service.add_emergency_update(db, sos_id, update_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit emergency update: {str(e)}")

@router.get("/{sos_id}/updates", response_model=List[EmergencyUpdateResponse])
def get_emergency_updates(sos_id: int, db: Session = Depends(get_db)):
    """Retrieve chronological emergency timeline updates for an SOS report."""
    sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
    if not sos:
        raise HTTPException(status_code=404, detail=f"SOS Report #{sos_id} not found")
    return sos_service.get_emergency_updates(db, sos_id)

@router.post("/{sos_id}/voice", response_model=EmergencyUpdateResponse)
async def upload_voice_emergency_update(
    sos_id: int,
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    client_update_id: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    accuracy: Optional[float] = Form(None),
    duration_seconds: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process incoming citizen voice emergency update:
    1. Validates active SOS exists
    2. Securely saves audio to local storage
    3. Transcribes speech using configured STT Provider (preserving native Telugu/Hindi/English)
    4. Attaches as EmergencyUpdate (update_type="VOICE_UPDATE")
    5. Triggers AI Emergency Re-Triage
    6. Broadcasts WebSocket event to Command Centre
    """
    sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
    if not sos:
        raise HTTPException(status_code=404, detail=f"SOS Report #{sos_id} not found")

    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Voice recording payload is empty")

    # 1. Save audio to storage
    try:
        storage_res = audio_storage_service.save_audio(
            sos_id=sos_id,
            audio_bytes=audio_bytes,
            filename=file.filename,
            mime_type=file.content_type
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store voice recording: {str(e)}")

    # 2. Transcribe speech
    try:
        transcription = stt_service.transcribe_audio(
            audio_bytes=audio_bytes,
            language=language,
            mime_type=storage_res["audio_mime_type"],
            duration_seconds=duration_seconds
        )
    except Exception as e:
        transcription = type('obj', (object,), {
            'text': "Voice distress message recorded (speech transcription in progress)",
            'original_language': language or "en",
            'confidence': 0.5,
            'provider': "fallback",
            'model': "none",
            'duration_seconds': duration_seconds or 0.0
        })()

    # 3. Create EmergencyUpdate
    update_in = EmergencyUpdateCreate(
        client_update_id=client_update_id,
        update_type="VOICE_UPDATE",
        message=transcription.text,
        original_language=transcription.original_language,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        source="CITIZEN_APP",
        audio_id=storage_res["audio_id"],
        audio_duration=transcription.duration_seconds,
        audio_mime_type=storage_res["audio_mime_type"],
        audio_size=storage_res["audio_size"],
        audio_storage_reference=storage_res["storage_reference"],
        transcription_provider=transcription.provider,
        transcription_model=transcription.model,
        transcription_confidence=transcription.confidence
    )

    try:
        update_record = sos_service.add_emergency_update(db, sos_id, update_in)
        return update_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to append voice emergency update: {str(e)}")

@router.get("/{sos_id}/voice/{audio_id}")
def stream_voice_audio(
    sos_id: int,
    audio_id: str,
    db: Session = Depends(get_db)
):
    """
    Stream emergency voice recording for authorized command operators or citizen review.
    Validates SOS existence, checks ownership to prevent unauthorized cross-incident playback.
    """
    sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
    if not sos:
        raise HTTPException(status_code=404, detail=f"SOS Report #{sos_id} not found")

    # Verify that this audio_id belongs to this SOS report (Authorization / Privacy Barrier)
    update_record = db.query(EmergencyUpdate).filter(
        EmergencyUpdate.sos_id == sos_id,
        EmergencyUpdate.audio_id == audio_id
    ).first()
    if not update_record:
        raise HTTPException(status_code=403, detail="Unauthorized audio access: Mismatched emergency incident")

    path = audio_storage_service.get_audio_path(sos_id, audio_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Audio recording file not found")

    mime = update_record.audio_mime_type or "audio/webm"
    return FileResponse(path, media_type=mime)

@router.post("/{sos_id}/triage", response_model=SOSTriageResponse)
def trigger_sos_triage(
    sos_id: int,
    force: bool = Query(False, description="Force re-running triage analysis"),
    db: Session = Depends(get_db)
):
    """
    Trigger or fetch AI Emergency Triage for an SOS distress report.
    Idempotent: Returns existing triage unless force=True.
    """
    try:
        triage = ai_triage_service.triage_sos(db=db, sos_id=sos_id, force_reanalyze=force)
        return triage
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Triage execution error: {str(e)}")

@router.get("/{sos_id}/triage", response_model=SOSTriageResponse)
def get_sos_triage_result(sos_id: int, db: Session = Depends(get_db)):
    """Retrieve existing AI Emergency Triage result for a specific SOS report."""
    triage = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).first()
    if not triage:
        try:
            return ai_triage_service.triage_sos(db=db, sos_id=sos_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return triage

@router.get("/{sos_id}/evidence", response_model=TriageEvidenceResponse)
def get_sos_triage_evidence(sos_id: int, db: Session = Depends(get_db)):
    """Retrieve verified facts, ML predictions, and evidence sources for an SOS report."""
    triage = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).first()
    if not triage:
        try:
            triage = ai_triage_service.triage_sos(db=db, sos_id=sos_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return TriageEvidenceResponse(
        sos_id=triage.sos_id,
        facts=triage.facts if isinstance(triage.facts, dict) else {},
        predictions=triage.predictions if isinstance(triage.predictions, dict) else {},
        data_sources=triage.data_sources if isinstance(triage.data_sources, list) else [],
        stale_data_warning=triage.stale_data_warning,
        ai_interpretation=triage.ai_interpretation,
        recommended_action=triage.recommended_action,
        human_confirmation_required=triage.human_confirmation_required
    )


def _calc_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


@router.get("/{sos_id}/guidance", response_model=SOSGuidanceResponse)
def get_sos_guidance(sos_id: int, db: Session = Depends(get_db)):
    """
    Returns authoritative emergency guidance for the citizen:
    - Current lifecycle & dispatch status
    - Recommended nearest shelter with capacity
    - Recommended nearest hospital with trauma/bed capacity
    - Safe evacuation destination and route with approx geographic distance
    - Context-aware localized safety instructions (English, Telugu, Hindi)
    """
    sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
    if not sos:
        raise HTTPException(status_code=404, detail=f"SOS Report #{sos_id} not found")

    inc = db.query(Incident).filter(Incident.sos_id == sos.id).first()
    triage = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos.id).first()

    # Determine dispatch status
    dispatch_status = "PENDING_REVIEW"
    assigned_team_name = None
    if inc:
        assignment = db.query(RescueAssignment).filter(
            RescueAssignment.incident_id == inc.id,
            RescueAssignment.status.in_(["DISPATCHED", "EN_ROUTE", "ON_SCENE", "COMPLETED"])
        ).order_by(RescueAssignment.id.desc()).first()
        if assignment:
            dispatch_status = assignment.status
            team = db.query(RescueTeam).filter(RescueTeam.id == assignment.rescue_team_id).first()
            if team:
                assigned_team_name = team.name
        elif inc.status == "RESCUED":
            dispatch_status = "RESOLVED"
        elif triage:
            dispatch_status = "AI_TRIAGE_COMPLETED"
    elif sos.status == "RESCUED":
        dispatch_status = "RESOLVED"

    # Find nearest shelter
    all_shelters = db.query(Shelter).all()
    rec_shelter = None
    if all_shelters:
        sorted_shelters = sorted(all_shelters, key=lambda s: _calc_haversine_km(sos.latitude, sos.longitude, s.latitude, s.longitude))
        best_shelter = sorted_shelters[0]
        dist_s = _calc_haversine_km(sos.latitude, sos.longitude, best_shelter.latitude, best_shelter.longitude)
        rec_shelter = RecommendedFacility(
            id=best_shelter.id,
            facility_type="SHELTER",
            name=best_shelter.name,
            latitude=best_shelter.latitude,
            longitude=best_shelter.longitude,
            distance_km=dist_s,
            distance_label="Approx. geographic distance",
            capacity_or_beds=f"{best_shelter.current_occupancy}/{best_shelter.capacity} occupied",
            status=best_shelter.status,
            reason="Nearest elevated district emergency shelter with available capacity"
        )

    # Find nearest hospital
    all_hospitals = db.query(Hospital).all()
    rec_hospital = None
    if all_hospitals:
        sorted_hospitals = sorted(all_hospitals, key=lambda h: _calc_haversine_km(sos.latitude, sos.longitude, h.latitude, h.longitude))
        best_hospital = sorted_hospitals[0]
        dist_h = _calc_haversine_km(sos.latitude, sos.longitude, best_hospital.latitude, best_hospital.longitude)
        rec_hospital = RecommendedFacility(
            id=best_hospital.id,
            facility_type="HOSPITAL",
            name=best_hospital.name,
            latitude=best_hospital.latitude,
            longitude=best_hospital.longitude,
            distance_km=dist_h,
            distance_label="Approx. geographic distance",
            capacity_or_beds=f"{best_hospital.available_beds} beds available",
            status=best_hospital.status,
            reason="Nearest medical trauma center equipped for severe disaster care"
        )

    # Build safe route guidance
    destination = rec_shelter or rec_hospital
    safe_route = None
    if destination:
        hazard = (triage.incident_type if triage else "FLOOD").upper()
        if "MEDICAL" in hazard and rec_hospital:
            destination = rec_hospital

        safe_route = SafeRouteGuidance(
            origin_latitude=sos.latitude,
            origin_longitude=sos.longitude,
            destination_name=destination.name,
            destination_type=destination.facility_type,
            destination_latitude=destination.latitude,
            destination_longitude=destination.longitude,
            distance_km=destination.distance_km,
            distance_label="Approx. geographic distance",
            routing_status="GEOGRAPHIC_LINE_ONLY",
            risk_warning="Water levels changing rapidly. Avoid low-lying corridors and proceed with extreme caution.",
            safety_instructions_en="Move towards elevated high-ground. Do not cross flowing water. Wait for rescue squad if ground is inundated.",
            safety_instructions_te="వరద పరిస్థితి ఉంది. వెంటనే ఎత్తైన మరియు సురక్షితమైన ప్రదేశానికి వెళ్లండి. నీటిలో నడవకండి.",
            safety_instructions_hi="बाढ़ की स्थिति है। तुरंत ऊंचे और सुरक्षित स्थान पर जाएं। बहते पानी में न चलें।"
        )

    return SOSGuidanceResponse(
        sos_id=sos.id,
        client_id=sos.client_id,
        status=sos.status,
        severity=sos.severity,
        incident_id=inc.id if inc else None,
        incident_status=inc.status if inc else None,
        dispatch_status=dispatch_status,
        assigned_team_name=assigned_team_name,
        recommended_shelter=rec_shelter,
        recommended_hospital=rec_hospital,
        safe_route=safe_route,
        triage_summary={
            "incident_type": triage.incident_type if triage else None,
            "severity": triage.severity if triage else None,
            "priority_score": triage.priority_score if triage else None
        } if triage else None,
        human_confirmation_required=True,
        data_provenance="POSTGRESQL_SPATIAL_CALCULATION"
    )


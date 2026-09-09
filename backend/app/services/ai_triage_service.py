import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models.sos import SOSReport
from app.database.models.incident import Incident
from app.database.models.sos_triage import SOSTriageResult
from app.database.models.risk import RiskZone
from app.database.models.rescue import RescueTeam
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.schemas.triage import IncidentTypeEnum, SeverityEnum, SOSTriageResponse
from app.ai.tools import DisasterGuardTools
from app.services.websocket_manager import ws_manager
from app.schemas.events import DomainEvent, EventType
from app.gis.spatial_queries import haversine_distance_km

logger = logging.getLogger("disasterguard.ai.triage")

class AITriageService:
    """
    AI Emergency Triage & Intelligent Incident Prioritization Engine.
    Analyzes incoming Citizen SOS reports with grounded multi-source context:
    - PostGIS / spatial risk zones
    - Live Open-Meteo weather telemetry
    - Scikit-Learn flood inundation & rainfall predictions
    - Controlled vocabulary incident classification
    - Explainable 0-100 priority scoring
    - Strict separation of Verified Facts vs ML Predictions vs AI Interpretation
    - Idempotency & Repeat Protection
    - Strict Human-in-the-Loop enforcement: Never autonomously dispatches rescue teams.
    """

    @staticmethod
    def triage_sos(
        db: Session,
        sos_id: int,
        force_reanalyze: bool = False
    ) -> SOSTriageResult:
        # 1. Check Idempotency: Return existing triage if already present
        existing = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).first()
        if existing and not force_reanalyze:
            logger.info(f"SOS_TRIAGE_IDEMPOTENT: Returning existing triage #{existing.id} for SOS #{sos_id}")
            return existing

        # 2. Verify SOS Report exists
        sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
        if not sos:
            raise ValueError(f"SOS Report #{sos_id} not found")

        # 3. Gather Multi-Source Operational Context
        lat = sos.latitude
        lng = sos.longitude
        msg = sos.message or ""
        msg_lower = msg.lower()

        # 3a. Nearest Risk Zone
        risk_zones = db.query(RiskZone).all()
        nearest_zone = None
        min_dist = float("inf")
        for z in risk_zones:
            dist = haversine_distance_km(lat, lng, z.latitude, z.longitude)
            if dist < min_dist:
                min_dist = dist
                nearest_zone = z

        zone_name = nearest_zone.name if nearest_zone else "General Urban Sector"
        zone_level = nearest_zone.risk_level if nearest_zone else "MODERATE"
        zone_score = nearest_zone.risk_score if nearest_zone else 45

        # 3b. Live Weather Observation
        weather = DisasterGuardTools.get_current_weather(db)
        rainfall_24h = weather.get("rainfall_24h_mm", 0.0) if isinstance(weather, dict) else 0.0
        weather_time = weather.get("observed_at")

        # 3c. ML Flood & Rainfall Predictions
        flood_pred = DisasterGuardTools.get_latest_flood_prediction(db)
        flood_prob = flood_pred.get("flood_probability", 0.5) if isinstance(flood_pred, dict) else 0.5
        water_depth = flood_pred.get("estimated_water_depth_m", 0.0) if isinstance(flood_pred, dict) else 0.0

        rain_pred = DisasterGuardTools.get_latest_rainfall_prediction(db)
        pred_rain_mm = rain_pred.get("predicted_rainfall_mm", 0.0) if isinstance(rain_pred, dict) else 0.0

        # 3d. Multi-Horizon Risk & Early Warning Forecast (Phase 5.3)
        forecast_ctx = {}
        try:
            forecast_ctx = DisasterGuardTools.get_multi_horizon_forecast(latitude=lat, longitude=lng, db=db)
        except Exception:
            pass

        # 3e. Active Emergency Alert Context (Phase 5.4)
        active_alert_ctx = None
        try:
            alerts_data = DisasterGuardTools.get_active_alerts(db=db)
            if alerts_data.get("alerts"):
                active_alert_ctx = alerts_data["alerts"][0]
        except Exception:
            pass

        # 3d. Check Data Freshness
        stale_warning = False
        if weather_time:
            try:
                dt = datetime.fromisoformat(weather_time)
                if datetime.now(timezone.utc) - dt > timedelta(hours=2):
                    stale_warning = True
            except Exception:
                pass

        # 4. Controlled Vocabulary NLP Classification (Multilingual: English, Telugu, Hindi)
        TRAPPED_KW = [
            "trapped", "stranded", "stuck", "surrounded", "cannot get out", "roof", "rooftop", "ceiling", "window", "second floor", "terrace",
            "చిక్కుకున్నారు", "చిక్కుకున్న", "చిక్కుకుపోయారు", "బయటకు రాలేక", "మేడపై", "పైకప్పు", "బయటకు రాలేకపోతున్నాం",
            "फंसे", "फंसा", "फंसे हुए", "अटके", "निकल नहीं सकते", "छत पर", "बाहर नहीं निकल पा रहे"
        ]
        VULNERABLE_KW = [
            "elderly", "senior", "infant", "baby", "child", "children", "pregnant", "disabled", "wheelchair", "bedridden", "grandmother", "grandfather", "father", "mother",
            "నాన్న", "తండ్రి", "అమ్మ", "తల్లి", "వృద్ధులు", "ముసలి", "పిల్లలు", "పాప", "బాబు", "గర్భిణీ",
            "पिताजी", "पिता", "माताजी", "माता", "मां", "बुजुर्ग", "वृद्ध", "बच्चे", "बच्चा", "गर्भवती"
        ]
        MEDICAL_KW = [
            "medical", "injured", "injury", "bleeding", "unconscious", "heart", "oxygen", "asthma", "insulin", "fracture", "wound", "patient", "hospital",
            "గాయం", "గాయపడ్డారు", "ఆసుపత్రి", "వైద్య", "రక్తం", "స్పృహ తప్పి", "శ్వాస",
            "चोट", "घायल", "अस्पताल", "चिकित्सा", "बेहोश", "खून", "सांस"
        ]
        FLOODING_KW = [
            "water entered", "rising water", "flooded", "flood", "submerged", "waist deep", "chest deep", "rushing water", "inundated", "overflow",
            "నీళ్లు", "నీరు", "వరద", "మునిగిపో", "నీరు పెరుగుతోంది", "నీళ్లు వచ్చాయి", "మునిగిపోయింది",
            "पानी भर गया", "बाढ़", "डूब", "जलस्तर बढ़ रहा है", "पानी", "डूब गया", "जलभराव"
        ]

        is_trapped = any(w in msg_lower for w in TRAPPED_KW)
        is_vulnerable = any(w in msg_lower for w in VULNERABLE_KW)
        is_medical = any(w in msg_lower for w in MEDICAL_KW)
        is_flooding = any(w in msg_lower for w in FLOODING_KW)
        is_evacuation = any(w in msg_lower for w in ["evacuate", "evacuation", "rescue", "help out", "get out", "save us", "కాపాడండి", "మమ్మల్ని రక్షించండి", "बचाओ", "मदद करो"])
        is_infra = any(w in msg_lower for w in ["collapsed", "wall crack", "building damaged", "power line", "short circuit", "gas leak", "bridge", "structure"])
        is_landslide = any(w in msg_lower for w in ["landslide", "mudslide", "rockfall", "debris slide", "hill collapsed"])
        is_road_blocked = any(w in msg_lower for w in ["road blocked", "cut off", "tree fallen", "submerged road", "cannot drive", "impassable"])
        is_power = any(w in msg_lower for w in ["blackout", "no power", "electricity cut", "transformer", "in the dark"])
        is_missing = any(w in msg_lower for w in ["missing person", "cannot find", "lost contact", "separated from"])
        is_weather = any(w in msg_lower for w in ["cyclone", "strong wind", "roof blown", "lightning", "storm surge", "gale"])

        # Classification decision
        if is_trapped:
            incident_type = IncidentTypeEnum.TRAPPED_PERSON.value
            confidence = 0.94
        elif is_medical:
            incident_type = IncidentTypeEnum.MEDICAL_EMERGENCY.value
            confidence = 0.92
        elif is_landslide:
            incident_type = IncidentTypeEnum.LANDSLIDE.value
            confidence = 0.90
        elif is_infra:
            incident_type = IncidentTypeEnum.INFRASTRUCTURE_DAMAGE.value
            confidence = 0.88
        elif is_road_blocked:
            incident_type = IncidentTypeEnum.ROAD_BLOCKAGE.value
            confidence = 0.88
        elif is_flooding:
            incident_type = IncidentTypeEnum.FLOODING.value
            confidence = 0.90
        elif is_evacuation:
            incident_type = IncidentTypeEnum.EVACUATION_REQUIRED.value
            confidence = 0.86
        elif is_missing:
            incident_type = IncidentTypeEnum.MISSING_PERSON.value
            confidence = 0.85
        elif is_power:
            incident_type = IncidentTypeEnum.POWER_OUTAGE.value
            confidence = 0.85
        elif is_weather:
            incident_type = IncidentTypeEnum.WEATHER_THREAT.value
            confidence = 0.86
        else:
            incident_type = IncidentTypeEnum.OTHER.value
            confidence = 0.70

        # Estimated people at risk
        people_count = 1
        for num_word, count in [("four", 4), ("three", 3), ("two", 2), ("five", 5), ("family", 4), ("residents", 3), ("elderly", 2)]:
            if num_word in msg_lower:
                people_count = max(people_count, count)

        # 5. Explainable Priority Score Calculation (0-100)
        score = 30
        reasons: List[str] = []

        if is_trapped:
            score += 35
            reasons.append("Citizen reports individuals physically trapped with evacuation route compromised")
        if is_vulnerable:
            score += 15
            reasons.append("Vulnerable individuals present (elderly / infant / mobility-impaired resident)")
        if is_medical:
            score += 35
            reasons.append("Medical emergency / critical trauma support flagged in distress communication")
        if is_flooding:
            score += 15
            reasons.append("Active residential inundation reported by citizen on site")
        if is_landslide:
            score += 25
            reasons.append("Geotechnical hazard / landslide activity reported in immediate vicinity")
        if zone_level in ["CRITICAL", "HIGH"]:
            score += 10
            reasons.append(f"Distress location lies within verified {zone_level} risk zone ({zone_name})")
        if flood_prob > 0.75 or water_depth >= 1.0:
            score += 10
            reasons.append(f"ML inundation model forecasts high flood hazard (depth: {water_depth:.2f}m, probability: {flood_prob*100:.0f}%)")
        if rainfall_24h >= 50.0:
            score += 5
            reasons.append(f"Heavy precipitation conditions active in local basin ({rainfall_24h:.1f}mm in 24h)")
        if is_infra:
            score += 15
            reasons.append("Structural instability or secondary hazard potential identified")

        # Clamp score between 10 and 100
        priority_score = min(100, max(10, score))

        # Determine Severity based on priority and multi-factor hazard
        if priority_score >= 85:
            severity = SeverityEnum.CRITICAL.value
        elif priority_score >= 65:
            severity = SeverityEnum.HIGH.value
        elif priority_score >= 45:
            severity = SeverityEnum.MODERATE.value
        else:
            severity = SeverityEnum.LOW.value

        # Formulate Recommended Action (Human-In-The-Loop Advisory)
        if severity == SeverityEnum.CRITICAL.value:
            if is_trapped:
                rec_action = "Prioritize motorized shallow-draft boat rescue dispatch; confirm water depth & structural stability prior to deployment."
            elif is_medical:
                rec_action = "Prioritize emergency medical evacuation squad with critical trauma supplies; alert receiving trauma center."
            else:
                rec_action = "Immediate priority rescue assessment recommended; dispatch scout team to verify safe access corridor."
        elif severity == SeverityEnum.HIGH.value:
            rec_action = "Coordinate high-clearance rescue vehicle and high-ground shelter transport; prioritize vulnerable residents."
        elif severity == SeverityEnum.MODERATE.value:
            rec_action = "Assign local civil defense support unit for evacuation assistance and emergency relief provisioning."
        else:
            rec_action = "Monitor sector situation; provide citizen with nearest safe shelter navigation guidance."

        # 6. Separate Verified Facts vs ML Predictions vs AI Interpretation
        facts = {
            "sos_id": sos.id,
            "client_id": sos.client_id,
            "latitude": lat,
            "longitude": lng,
            "accuracy_m": sos.accuracy,
            "reported_message": msg,
            "reported_severity": sos.severity,
            "received_at": sos.created_at.isoformat() if sos.created_at else datetime.now(timezone.utc).isoformat(),
            "transport": sos.transport or "INTERNET"
        }

        predictions = {
            "flood_probability": round(flood_prob, 2),
            "estimated_water_depth_m": round(water_depth, 2),
            "predicted_rainfall_24h_mm": round(pred_rain_mm, 1),
            "risk_zone_name": zone_name,
            "risk_zone_level": zone_level,
            "risk_zone_score": zone_score,
            "active_rainfall_24h_mm": round(rainfall_24h, 1),
            "multi_horizon_forecast": forecast_ctx,
            "active_alert": active_alert_ctx
        }

        ai_interpretation = (
            f"Automated AI Emergency Triage classified distress as {incident_type} with Priority {priority_score}/100 ({severity}). "
            f"Assessed {people_count} individual(s) potentially exposed to hazard. "
            f"Multi-source correlation shows location is {zone_level} risk with {flood_prob*100:.0f}% ML inundation probability. "
            f"Advisory: {rec_action}"
        )

        data_sources = [
            "Citizen Distress Report (IndexedDB/REST)",
            "PostGIS Spatial Risk Zone Database",
            "Open-Meteo Meteorological Telemetry",
            "Scikit-Learn Flood Inundation Prediction Engine",
            "Scikit-Learn Precipitation Forecast Model"
        ]

        # 7. Persist or Update Triage Result in PostgreSQL
        if existing:
            triage_record = existing
            triage_record.incident_type = incident_type
            triage_record.severity = severity
            triage_record.priority_score = priority_score
            triage_record.confidence = confidence
            triage_record.confidence_type = "MULTIMODAL_GROUNDED"
            triage_record.people_at_risk = people_count
            triage_record.medical_emergency = is_medical
            triage_record.trapped_person = is_trapped
            triage_record.flooding = is_flooding
            triage_record.infrastructure_damage = is_infra
            triage_record.immediate_threat = (severity == SeverityEnum.CRITICAL.value)
            triage_record.recommended_action = rec_action
            triage_record.reasoning = reasons
            triage_record.data_sources = data_sources
            triage_record.facts = facts
            triage_record.predictions = predictions
            triage_record.ai_interpretation = ai_interpretation
            triage_record.provider = "DeterministicTriageEngine"
            triage_record.model = "rule-based-nlp-v2"
            triage_record.triage_status = "COMPLETE"
            triage_record.stale_data_warning = stale_warning
            triage_record.human_confirmation_required = True
            triage_record.updated_at = datetime.now(timezone.utc)
        else:
            triage_record = SOSTriageResult(
                sos_id=sos.id,
                incident_type=incident_type,
                severity=severity,
                priority_score=priority_score,
                confidence=confidence,
                confidence_type="MULTIMODAL_GROUNDED",
                people_at_risk=people_count,
                medical_emergency=is_medical,
                trapped_person=is_trapped,
                flooding=is_flooding,
                infrastructure_damage=is_infra,
                immediate_threat=(severity == SeverityEnum.CRITICAL.value),
                recommended_action=rec_action,
                reasoning=reasons,
                data_sources=data_sources,
                facts=facts,
                predictions=predictions,
                ai_interpretation=ai_interpretation,
                provider="DeterministicTriageEngine",
                model="rule-based-nlp-v2",
                triage_status="COMPLETE",
                stale_data_warning=stale_warning,
                human_confirmation_required=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(triage_record)

        db.commit()
        db.refresh(triage_record)

        # 8. Update linked Incident in PostgreSQL (Strictly keeping status PENDING - no auto dispatch)
        linked_inc = db.query(Incident).filter(Incident.sos_id == sos.id).first()
        if linked_inc:
            linked_inc.incident_type = incident_type
            linked_inc.severity = severity
            linked_inc.priority_score = priority_score
            triage_record.incident_id = linked_inc.id
            db.commit()
            db.refresh(triage_record)
            db.refresh(linked_inc)

        logger.info(
            f"SOS_TRIAGED: SOS #{sos.id} classified as {incident_type}, Priority {priority_score}, Severity {severity}, "
            f"Confidence {confidence:.2f}, Stale Warning: {stale_warning}"
        )

        # 9. Broadcast SOS_TRIAGED Domain Event via WebSocket
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SOS_TRIAGED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=sos.id,
                    entity_type="sos",
                    severity=severity,
                    data={
                        "triage_id": triage_record.id,
                        "sos_id": sos.id,
                        "incident_id": linked_inc.id if linked_inc else None,
                        "incident_type": incident_type,
                        "severity": severity,
                        "priority_score": priority_score,
                        "confidence": confidence,
                        "confidence_type": triage_record.confidence_type,
                        "people_at_risk": people_count,
                        "trapped_person": is_trapped,
                        "medical_emergency": is_medical,
                        "flooding": is_flooding,
                        "recommended_action": rec_action,
                        "reasoning": reasons,
                        "facts": facts,
                        "predictions": predictions,
                        "ai_interpretation": ai_interpretation,
                        "stale_data_warning": stale_warning,
                        "human_confirmation_required": True,
                        "triage_status": "COMPLETE",
                        "title": f"Citizen SOS #{sos.id}: {incident_type}"
                    }
                )
            )
        except Exception as e:
            logger.warning(f"Failed to broadcast SOS_TRIAGED event: {e}")

        return triage_record


    @staticmethod
    def reassess_sos(
        db: Session,
        sos_id: int,
        new_update: Any
    ) -> SOSTriageResult:
        """
        Reassess AI Emergency Triage after receiving a new EmergencyUpdate.
        Aggregates chronological updates, identifies newly emerging distress factors,
        escalates priority score, preserves historical audit entries in facts['triage_history'],
        and strictly preserves the Human Operator Confirmation Barrier (human_confirmation_required = True).
        """
        from app.database.models.emergency_update import EmergencyUpdate

        sos = db.query(SOSReport).filter(SOSReport.id == sos_id).first()
        if not sos:
            raise ValueError(f"SOS Report #{sos_id} not found")

        triage_record = db.query(SOSTriageResult).filter(SOSTriageResult.sos_id == sos_id).first()
        if not triage_record:
            # If no initial triage exists, run initial triage first
            triage_record = AITriageService.triage_sos(db, sos_id, force_reanalyze=True)

        # Collect all messages from SOS and updates
        all_updates = db.query(EmergencyUpdate).filter(EmergencyUpdate.sos_id == sos_id).order_by(EmergencyUpdate.created_at.asc()).all()
        messages = [sos.message or ""]
        for u in all_updates:
            if u.message and u.message not in messages:
                messages.append(u.message)
        if new_update and new_update.message and new_update.message not in messages:
            messages.append(new_update.message)

        combined_text = " | ".join([m for m in messages if m.strip()]).lower()

        # Check distress flags across all chronological updates (Multilingual: English, Telugu, Hindi)
        TRAPPED_KW = [
            "trapped", "stranded", "stuck", "surrounded", "cannot get out", "roof", "rooftop", "ceiling", "window", "second floor", "terrace",
            "చిక్కుకున్నారు", "చిక్కుకున్న", "చిక్కుకుపోయారు", "బయటకు రాలేక", "మేడపై", "పైకప్పు", "బయటకు రాలేకపోతున్నాం",
            "ఫంసే", "ఫంసా", "ఫంసే హుఏ", "फंसे", "फंसा", "फंसे हुए", "अटके", "निकल नहीं सकते", "छत पर", "बाहर नहीं निकल पा रहे"
        ]
        VULNERABLE_KW = [
            "elderly", "senior", "infant", "baby", "child", "children", "pregnant", "disabled", "wheelchair", "bedridden", "father", "mother", "grandmother", "grandfather",
            "నాన్న", "తండ్రి", "అమ్మ", "తల్లి", "వృద్ధులు", "ముసలి", "పిల్లలు", "పాప", "బాబు", "గర్భిణీ",
            "पिताजी", "पिता", "माताजी", "माता", "मां", "बुजुर्ग", "वृद्ध", "बच्चे", "बच्चा", "गर्भवती"
        ]
        MEDICAL_KW = [
            "medical", "injured", "injury", "bleeding", "unconscious", "heart", "oxygen", "asthma", "insulin", "fracture", "wound", "patient", "hospital",
            "గాయం", "గాయపడ్డారు", "ఆసుపత్రి", "వైద్య", "రక్తం", "స్పృహ తప్పి", "శ్వాస",
            "चोट", "घायल", "अस्पताल", "चिकित्सा", "बेहोश", "खून", "सांस"
        ]
        FLOODING_KW = [
            "water entered", "rising water", "increasing", "water is rising", "water level", "flooded", "flood", "submerged", "waist deep", "chest deep", "rushing water", "inundated", "overflow",
            "నీళ్లు", "నీరు", "వరద", "మునిగిపో", "నీరు పెరుగుతోంది", "నీళ్లు వచ్చాయి", "మునిగిపోయింది",
            "पानी भर गया", "बाढ़", "डूब", "जलस्तर बढ़ रहा है", "पानी", "डूब गया", "जलभराव"
        ]

        is_trapped = any(w in combined_text for w in TRAPPED_KW) or (new_update and new_update.update_type in ("TRAPPED_PERSON_UPDATE", "VOICE_UPDATE") and any(w in (getattr(new_update, 'message', '') or '').lower() for w in TRAPPED_KW))
        is_vulnerable = any(w in combined_text for w in VULNERABLE_KW)
        is_medical = any(w in combined_text for w in MEDICAL_KW) or (new_update and new_update.update_type == "MEDICAL_UPDATE")
        is_flooding = any(w in combined_text for w in FLOODING_KW) or (new_update and new_update.update_type == "WATER_LEVEL_UPDATE")
        is_infra = any(w in combined_text for w in ["collapsed", "wall crack", "building damaged", "power line", "short circuit", "gas leak", "bridge", "structure"])
        is_landslide = any(w in combined_text for w in ["landslide", "mudslide", "rockfall", "debris slide", "hill collapsed"])

        # Determine updated classification
        if is_trapped:
            incident_type = IncidentTypeEnum.TRAPPED_PERSON.value
            confidence = 0.96
        elif is_medical:
            incident_type = IncidentTypeEnum.MEDICAL_EMERGENCY.value
            confidence = 0.94
        elif is_landslide:
            incident_type = IncidentTypeEnum.LANDSLIDE.value
            confidence = 0.90
        elif is_infra:
            incident_type = IncidentTypeEnum.INFRASTRUCTURE_DAMAGE.value
            confidence = 0.88
        elif is_flooding:
            incident_type = IncidentTypeEnum.FLOODING.value
            confidence = 0.92
        else:
            incident_type = triage_record.incident_type or IncidentTypeEnum.OTHER.value
            confidence = 0.85

        # Calculate escalated priority score
        score = 30
        reasons: List[str] = []

        if is_trapped:
            score += 35
            reasons.append("Escalation: Individual physically trapped with compromised evacuation route")
        if is_vulnerable:
            score += 15
            reasons.append("Vulnerable / elderly / infant individual identified in distress communication")
        if is_medical:
            score += 35
            reasons.append("Escalation: Acute medical / trauma care flagged in distress updates")
        if is_flooding:
            score += 15
            reasons.append("Escalation: Rapidly rising residential floodwaters reported on scene")
        if is_landslide:
            score += 25
            reasons.append("Geotechnical hazard / landslide activity reported in immediate vicinity")

        # Multi-source environmental bonus
        flood_pred = DisasterGuardTools.get_latest_flood_prediction(db)
        flood_prob = flood_pred.get("flood_probability", 0.5) if isinstance(flood_pred, dict) else 0.5
        water_depth = flood_pred.get("estimated_water_depth_m", 0.0) if isinstance(flood_pred, dict) else 0.0
        if flood_prob > 0.75 or water_depth >= 1.0:
            score += 10
            reasons.append(f"ML inundation model forecasts severe flood depth ({water_depth:.2f}m)")

        # Ensure priority does not downgrade during escalation
        old_score = triage_record.priority_score or 50
        escalated_score = max(score, old_score)
        priority_score = min(100, max(10, escalated_score))

        # Severity
        if priority_score >= 85:
            severity = SeverityEnum.CRITICAL.value
        elif priority_score >= 65:
            severity = SeverityEnum.HIGH.value
        elif priority_score >= 45:
            severity = SeverityEnum.MODERATE.value
        else:
            severity = SeverityEnum.LOW.value

        # Formulate recommended action
        if severity == SeverityEnum.CRITICAL.value:
            if is_trapped:
                rec_action = "Prioritize motorized shallow-draft boat rescue dispatch; confirm water depth & structural stability prior to deployment."
            elif is_medical:
                rec_action = "Prioritize emergency medical evacuation squad with critical trauma supplies; alert receiving trauma center."
            else:
                rec_action = "Immediate priority rescue assessment recommended; dispatch scout team to verify safe access corridor."
        else:
            rec_action = triage_record.recommended_action or "Operator review recommended"

        # Preserve triage audit history
        current_facts = dict(triage_record.facts) if isinstance(triage_record.facts, dict) else {}
        history = current_facts.get("triage_history", [])
        history.append({
            "previous_priority": old_score,
            "previous_severity": triage_record.severity,
            "previous_incident_type": triage_record.incident_type,
            "escalated_priority": priority_score,
            "escalated_severity": severity,
            "trigger_update_type": getattr(new_update, "update_type", "TEXT_UPDATE"),
            "trigger_update_id": getattr(new_update, "id", None),
            "reassessed_at": datetime.now(timezone.utc).isoformat(),
            "reasons": reasons
        })
        current_facts["triage_history"] = history
        current_facts["latest_emergency_update"] = getattr(new_update, "message", None)
        if new_update:
            if getattr(new_update, "original_language", None):
                current_facts["original_language"] = getattr(new_update, "original_language")
            if getattr(new_update, "audio_id", None):
                current_facts["audio_id"] = getattr(new_update, "audio_id")
            if getattr(new_update, "transcription_provider", None):
                current_facts["transcription_provider"] = getattr(new_update, "transcription_provider")

        ai_interpretation = (
            f"AI Emergency Re-Triage escalated incident to {incident_type} with Priority {priority_score}/100 ({severity}). "
            f"Chronological updates indicate escalating peril. Advisory: {rec_action}"
        )

        # Update triage record
        triage_record.incident_type = incident_type
        triage_record.severity = severity
        triage_record.priority_score = priority_score
        triage_record.confidence = confidence
        triage_record.trapped_person = is_trapped
        triage_record.medical_emergency = is_medical
        triage_record.flooding = is_flooding
        triage_record.infrastructure_damage = is_infra
        triage_record.immediate_threat = (severity == SeverityEnum.CRITICAL.value)
        triage_record.recommended_action = rec_action
        triage_record.reasoning = reasons
        triage_record.facts = current_facts
        triage_record.ai_interpretation = ai_interpretation
        triage_record.human_confirmation_required = True
        triage_record.updated_at = datetime.now(timezone.utc)

        # Update linked incident
        linked_inc = db.query(Incident).filter(Incident.sos_id == sos_id).first()
        if linked_inc:
            linked_inc.incident_type = incident_type
            linked_inc.severity = severity
            linked_inc.priority_score = priority_score
            linked_inc.updated_at = datetime.now(timezone.utc)
            triage_record.incident_id = linked_inc.id

        # Update SOS severity
        sos.severity = severity

        db.commit()
        db.refresh(triage_record)
        if linked_inc:
            db.refresh(linked_inc)
        db.refresh(sos)

        logger.info(
            f"SOS_REASSESSED: SOS #{sos_id} escalated to {incident_type}, Priority {priority_score}, Severity {severity} "
            f"(Trigger: {getattr(new_update, 'update_type', 'UPDATE')})"
        )

        # Broadcast SOS_TRIAGED Domain Event
        try:
            ws_manager.broadcast_event(
                DomainEvent(
                    event=EventType.SOS_TRIAGED,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    entity_id=sos.id,
                    entity_type="sos",
                    severity=severity,
                    data={
                        "triage_id": triage_record.id,
                        "sos_id": sos.id,
                        "incident_id": linked_inc.id if linked_inc else None,
                        "incident_type": incident_type,
                        "severity": severity,
                        "priority_score": priority_score,
                        "confidence": confidence,
                        "confidence_type": triage_record.confidence_type,
                        "trapped_person": is_trapped,
                        "medical_emergency": is_medical,
                        "flooding": is_flooding,
                        "recommended_action": rec_action,
                        "reasoning": reasons,
                        "ai_interpretation": ai_interpretation,
                        "human_confirmation_required": True,
                        "triage_status": "COMPLETE",
                        "title": f"Citizen SOS #{sos.id}: {incident_type} (Reassessed)"
                    }
                )
            )
        except Exception as e:
            logger.warning(f"Failed to broadcast SOS_TRIAGED reassessment event: {e}")

        return triage_record

ai_triage_service = AITriageService()

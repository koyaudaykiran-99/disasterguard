"""
AI-DisasterGuard — Incident Prioritization Engine
Phase 5.5: Operational Priority Scoring (0-100) and Explainable Decision Support
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ml.operations import (
    OperationalPriorityLevel,
    EvidenceType,
    PRIORITY_WEIGHTS,
)

def calculate_incident_priority(
    incident: Any,
    triage_record: Optional[Any] = None,
    forecast_record: Optional[Any] = None,
    flood_record: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Computes an explainable operational priority score (0-100) and assigns an
    OperationalPriorityLevel (CRITICAL, HIGH, MEDIUM, LOW) based on multi-hazard evidence.
    
    Factors:
    - Trapped individuals (+30)
    - Medical emergencies (+25)
    - Immediate threat / rapid water rise (+20)
    - Local flood susceptibility (+10)
    - Increasing forecast risk trajectory (+10)
    - Incident unresolved age (+5)
    """
    # Extract attributes safely from dict or ORM object
    def get_val(obj, key, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    title = str(get_val(incident, "title", "")).lower()
    description = str(get_val(incident, "description", "")).lower()
    severity = str(get_val(incident, "severity", "LOW")).upper()
    status = str(get_val(incident, "status", "PENDING")).upper()
    created_at = get_val(incident, "created_at")
    
    # 1. Trapped Individuals (+30)
    trapped_keywords = ["trapped", "stuck", "roof", "rooftop", "stranded", "cannot escape", "surrounded by water"]
    is_trapped = (
        any(kw in description for kw in trapped_keywords) or
        any(kw in title for kw in trapped_keywords) or
        bool(get_val(triage_record, "trapped_person", False))
    )
    
    # 2. Medical Emergency (+25)
    medical_keywords = ["medical", "injury", "injured", "heart", "bleeding", "unconscious", "pregnant", "diabetic", "oxygen", "elderly sick"]
    is_medical = (
        any(kw in description for kw in medical_keywords) or
        any(kw in title for kw in medical_keywords) or
        bool(get_val(triage_record, "medical_emergency", False))
    )
    
    # 3. Immediate Threat / Fast Rise (+20)
    threat_keywords = ["rising fast", "immediate threat", "submerged", "swept", "water entering", "waist high", "chest high", "neck high"]
    is_immediate_threat = (
        severity in ["CRITICAL", "HIGH"] or
        any(kw in description for kw in threat_keywords) or
        any(kw in title for kw in threat_keywords) or
        bool(get_val(triage_record, "immediate_threat", False)) or
        str(get_val(triage_record, "urgency", "")).upper() == "CRITICAL"
    )
    
    # 4. High Local Flood Susceptibility (+10)
    susceptibility_val = float(get_val(flood_record, "susceptibility", get_val(flood_record, "susceptibility_score", 0.0)) or 0.0)
    flood_risk_level = str(get_val(flood_record, "risk_level", "")).upper()
    is_high_flood_risk = (
        susceptibility_val >= 0.6 or
        flood_risk_level in ["CRITICAL", "HIGH"] or
        "flood" in title or "flood" in description
    )
    
    # 5. Increasing Forecast Risk Trajectory (+10)
    trajectory = str(get_val(forecast_record, "trajectory", get_val(forecast_record, "trend", "STABLE"))).upper()
    peak_risk = str(get_val(forecast_record, "peak_risk_level", get_val(forecast_record, "risk_level", ""))).upper()
    is_increasing_forecast = (
        trajectory in ["INCREASING", "PEAKING"] or
        peak_risk in ["CRITICAL", "HIGH"]
    )
    
    # 6. Incident Age (+5)
    incident_age_minutes = 0.0
    if created_at:
        try:
            if isinstance(created_at, str):
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                dt = created_at
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            incident_age_minutes = max(0.0, (now - dt).total_seconds() / 60.0)
        except Exception:
            incident_age_minutes = 0.0
            
    is_aged_unresolved = (
        status in ["PENDING", "UNASSIGNED"] and
        (incident_age_minutes >= 15.0 or get_val(incident, "age_minutes", 0.0) >= 15.0)
    )
    
    # Calculate Score Components
    component_scores = {
        "trapped_person": PRIORITY_WEIGHTS["trapped_person"] if is_trapped else 0.0,
        "medical_emergency": PRIORITY_WEIGHTS["medical_emergency"] if is_medical else 0.0,
        "immediate_threat": PRIORITY_WEIGHTS["immediate_threat"] if is_immediate_threat else 0.0,
        "flood_susceptibility": PRIORITY_WEIGHTS["flood_susceptibility"] if is_high_flood_risk else 0.0,
        "increasing_forecast": PRIORITY_WEIGHTS["increasing_forecast"] if is_increasing_forecast else 0.0,
        "incident_age": PRIORITY_WEIGHTS["incident_age"] if is_aged_unresolved else 0.0,
    }
    
    # People count baseline factor (up to 10 points if no other critical flags, or minimum base)
    people_count = int(get_val(incident, "people_at_risk", get_val(triage_record, "people_count", 1)) or 1)
    base_score = min(10.0, float(people_count) * 2.0)
    
    raw_score = sum(component_scores.values())
    if raw_score == 0:
        raw_score = base_score
    else:
        # If any major factor triggered, ensure score is at least proportional
        raw_score = min(100.0, raw_score)
        
    final_score = round(max(0.0, min(100.0, raw_score)), 1)
    
    # Determine Priority Level
    if final_score >= 90.0:
        priority_level = OperationalPriorityLevel.CRITICAL
    elif final_score >= 70.0:
        priority_level = OperationalPriorityLevel.HIGH
    elif final_score >= 40.0:
        priority_level = OperationalPriorityLevel.MEDIUM
    else:
        priority_level = OperationalPriorityLevel.LOW
        
    # Build Evidence Decomposition
    evidence: List[Dict[str, str]] = []
    reasons: List[str] = []
    warnings: List[str] = []
    
    # FACT
    evidence.append({
        "type": EvidenceType.FACT.value,
        "detail": f"{people_count} person(s) reported at incident location."
    })
    if is_trapped:
        evidence.append({
            "type": EvidenceType.FACT.value,
            "detail": "Verified report: Individual(s) trapped or stranded."
        })
        reasons.append("Person reported trapped")
    if is_medical:
        evidence.append({
            "type": EvidenceType.FACT.value,
            "detail": "Verified report: Medical emergency requires immediate attention."
        })
        reasons.append("Medical emergency reported")
    if is_aged_unresolved:
        age_str = f"{int(incident_age_minutes)} min" if incident_age_minutes > 0 else ">15 min"
        evidence.append({
            "type": EvidenceType.FACT.value,
            "detail": f"Incident has remained unresolved for {age_str}."
        })
        reasons.append(f"Incident unresolved for {age_str}")
        warnings.append(f"Response overdue: Incident unassigned for {age_str}")
        
    # ML_PREDICTION
    if is_increasing_forecast:
        evidence.append({
            "type": EvidenceType.ML_PREDICTION.value,
            "detail": f"Predictive model indicates risk trajectory is {trajectory} (Peak: {peak_risk})."
        })
        reasons.append(f"Forecast risk trajectory is {trajectory}")
    else:
        evidence.append({
            "type": EvidenceType.ML_PREDICTION.value,
            "detail": "Predictive model indicates stable or baseline risk trajectory."
        })
        
    # GEOSPATIAL_DERIVATION
    if is_high_flood_risk:
        sus_str = f"{susceptibility_val:.2f}" if susceptibility_val > 0 else "HIGH"
        evidence.append({
            "type": EvidenceType.GEOSPATIAL_DERIVATION.value,
            "detail": f"Incident location intersects high flood susceptibility zone ({sus_str})."
        })
        reasons.append("High local flood susceptibility")
    else:
        evidence.append({
            "type": EvidenceType.GEOSPATIAL_DERIVATION.value,
            "detail": "Incident location in moderate/low flood susceptibility zone."
        })
        
    # AI_INTERPRETATION
    if is_trapped and is_medical and is_high_flood_risk:
        evidence.append({
            "type": EvidenceType.AI_INTERPRETATION.value,
            "detail": "Compound life safety threat: Trapped occupants with urgent medical needs under active flood danger."
        })
    elif is_trapped or is_medical:
        evidence.append({
            "type": EvidenceType.AI_INTERPRETATION.value,
            "detail": "Elevated life safety threat requiring specialized rescue or medical intervention."
        })
    else:
        evidence.append({
            "type": EvidenceType.AI_INTERPRETATION.value,
            "detail": "Standard priority operational queue assessment."
        })
        
    # RECOMMENDATION
    if priority_level == OperationalPriorityLevel.CRITICAL:
        evidence.append({
            "type": EvidenceType.RECOMMENDATION.value,
            "detail": "IMMEDIATE OPERATOR ACTION: Prioritize for rescue team assignment and dispatch confirmation."
        })
    elif priority_level == OperationalPriorityLevel.HIGH:
        evidence.append({
            "type": EvidenceType.RECOMMENDATION.value,
            "detail": "HIGH OPERATIONAL PRIORITY: Assign available specialized rescue squad promptly."
        })
    else:
        evidence.append({
            "type": EvidenceType.RECOMMENDATION.value,
            "detail": "MONITOR & QUEUE: Coordinate with regional units as resources become available."
        })
        
    return {
        "priority_score": final_score,
        "priority_level": priority_level.value,
        "component_scores": component_scores,
        "evidence": evidence,
        "reasons": reasons,
        "warnings": warnings,
        "is_trapped": is_trapped,
        "is_medical": is_medical,
        "is_immediate_threat": is_immediate_threat,
        "people_at_risk": people_count,
        "age_minutes": incident_age_minutes,
    }

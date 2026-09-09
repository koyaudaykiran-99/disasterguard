from fastapi import APIRouter, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import jwt

from app.database.database import get_db
from app.core.config import settings
from app.ai.agent import ai_agent
from app.ai.schemas import (
    AIEmergencyRequest, AIEmergencyResponse,
    EmergencyBriefingResponse,
    IncidentAnalysisRequest, IncidentAnalysisResponse,
    RiskExplanationRequest, RiskExplanationResponse,
    ShelterRecommendationRequest, ShelterRecommendationResponse,
    RescueAnalysisResponse
)
from app.schemas.ai import (
    PersonalizedSafetyRequest, PersonalizedSafetyResponse,
    AlertExplanationRequest, AlertExplanationResponse,
    RiskInterpretationRequest, RiskInterpretationResponse
)
from app.services.ai_service import ai_service

router = APIRouter()

def extract_role(authorization: Optional[str] = None, fallback_role: Optional[str] = "OPERATOR") -> str:
    """Extract authenticated user role from JWT token, with graceful fallback."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if token != "demo":
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                return payload.get("role", fallback_role or "OPERATOR").upper()
            except Exception:
                pass
    return (fallback_role or "OPERATOR").upper()

@router.post("/chat", response_model=AIEmergencyResponse)
async def chat_assistant(
    req: AIEmergencyRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Conversational AI Emergency Agent.
    Grounded in live PostgreSQL facts, PostGIS risk zones, and Scikit-Learn predictions.
    Human-in-the-loop decision support with role-based access control.
    """
    try:
        user_role = extract_role(authorization, req.role)
        req.role = user_role
        return await ai_agent.chat(req, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@router.get("/briefing")
@router.post("/briefing")
async def generate_briefing(
    role: Optional[str] = Query("OPERATOR"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Generate structured executive disaster briefing across all operational sectors with 5-part evidence taxonomy."""
    try:
        from app.services.situational_awareness_service import situational_awareness_service
        user_role = extract_role(authorization, role)
        return situational_awareness_service.generate_ai_briefing(db, role=user_role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Briefing generation error: {str(e)}")

@router.post("/analyze-incident", response_model=IncidentAnalysisResponse)
async def analyze_incident(
    req: IncidentAnalysisRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Deep incident analysis with tactical rescue assignment recommendations."""
    try:
        user_role = extract_role(authorization, req.role)
        return await ai_agent.analyze_incident(req.incident_id, db, role=user_role)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incident analysis error: {str(e)}")

@router.post("/explain-risk", response_model=RiskExplanationResponse)
async def explain_risk(
    req: RiskExplanationRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Explain multi-factor risk calculations (weather -> ML flood probability -> demographic exposure)."""
    try:
        return await ai_agent.explain_risk(db, zone_id=req.zone_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk explanation error: {str(e)}")

@router.post("/recommend-shelter", response_model=ShelterRecommendationResponse)
async def recommend_shelter(
    req: ShelterRecommendationRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Spatial risk-aware evacuation shelter recommendations."""
    try:
        user_role = extract_role(authorization, req.role)
        return await ai_agent.recommend_shelter(req.latitude, req.longitude, db, role=user_role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shelter recommendation error: {str(e)}")

@router.post("/rescue-analysis", response_model=RescueAnalysisResponse)
async def rescue_analysis(
    role: Optional[str] = Query("OPERATOR"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Rescue operations analysis matching unassigned incidents to field teams."""
    try:
        user_role = extract_role(authorization, role)
        return await ai_agent.analyze_rescue(db, role=user_role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rescue analysis error: {str(e)}")

@router.post("/safety-instructions", response_model=PersonalizedSafetyResponse)
async def generate_safety_instructions(req: PersonalizedSafetyRequest):
    """Generate dynamic, customized safety protocol and evacuation checklist."""
    try:
        return await ai_service.generate_safety_instructions(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety instruction generation error: {str(e)}")

@router.post("/explain-alert", response_model=AlertExplanationResponse)
async def explain_alert(req: AlertExplanationRequest):
    """Convert technical alert into clear, human-friendly explanation."""
    try:
        return await ai_service.explain_alert(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert explanation error: {str(e)}")

@router.post("/interpret-risk", response_model=RiskInterpretationResponse)
async def interpret_risk(req: RiskInterpretationRequest):
    """Deep AI breakdown of composite risk score."""
    try:
        return await ai_service.interpret_risk(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk interpretation error: {str(e)}")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.risk import RiskZone
from app.database.models.incident import Incident
from app.database.models.sos import SOSReport
from app.database.models.shelter import Shelter
from app.database.models.hospital import Hospital
from app.database.models.rescue import RescueTeam
from app.gis.geojson import create_point_feature, create_feature_collection
from typing import Dict, Any

router = APIRouter()

@router.get("/risk-zones")
def get_map_risk_zones(db: Session = Depends(get_db)) -> Dict[str, Any]:
    zones = db.query(RiskZone).all()
    features = [
        create_point_feature(z.id, z.latitude, z.longitude, {
            "name": z.name, "risk_level": z.risk_level, "risk_score": z.risk_score, "population": z.population_estimate
        }) for z in zones
    ]
    return create_feature_collection(features)

@router.get("/incidents")
def get_map_incidents(db: Session = Depends(get_db)) -> Dict[str, Any]:
    incidents = db.query(Incident).all()
    features = [
        create_point_feature(i.id, i.latitude, i.longitude, {
            "title": i.title, "incident_type": i.incident_type, "severity": i.severity, "status": i.status, "priority_score": i.priority_score
        }) for i in incidents
    ]
    return create_feature_collection(features)

@router.get("/sos")
def get_map_sos(db: Session = Depends(get_db)) -> Dict[str, Any]:
    sos_list = db.query(SOSReport).filter(SOSReport.status != "RESCUED").all()
    features = [
        create_point_feature(s.id, s.latitude, s.longitude, {
            "message": s.message, "severity": s.severity, "status": s.status, "created_at": str(s.created_at)
        }) for s in sos_list
    ]
    return create_feature_collection(features)

@router.get("/shelters")
def get_map_shelters(db: Session = Depends(get_db)) -> Dict[str, Any]:
    shelters = db.query(Shelter).all()
    features = [
        create_point_feature(s.id, s.latitude, s.longitude, {
            "name": s.name, "capacity": s.capacity, "occupancy": s.current_occupancy, "status": s.status, "contact": s.contact
        }) for s in shelters
    ]
    return create_feature_collection(features)

@router.get("/hospitals")
def get_map_hospitals(db: Session = Depends(get_db)) -> Dict[str, Any]:
    hospitals = db.query(Hospital).all()
    features = [
        create_point_feature(h.id, h.latitude, h.longitude, {
            "name": h.name, "beds": h.available_beds, "status": h.status, "contact": h.contact
        }) for h in hospitals
    ]
    return create_feature_collection(features)

@router.get("/rescue-teams")
def get_map_rescue_teams(db: Session = Depends(get_db)) -> Dict[str, Any]:
    teams = db.query(RescueTeam).all()
    features = [
        create_point_feature(t.id, t.latitude, t.longitude, {
            "name": t.name, "team_size": t.team_size, "vehicle_type": t.vehicle_type, "status": t.status
        }) for t in teams
    ]
    return create_feature_collection(features)

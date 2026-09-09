from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalResponse
from app.gis.spatial_queries import haversine_distance_km
from typing import List

router = APIRouter()

@router.get("", response_model=List[HospitalResponse])
@router.get("/", response_model=List[HospitalResponse])
def get_all_hospitals(db: Session = Depends(get_db)):
    """Retrieve emergency hospitals."""
    return db.query(Hospital).all()

@router.get("/nearby", response_model=List[HospitalResponse])
def get_nearby_hospitals(
    lat: float = Query(13.0827),
    lng: float = Query(80.2707),
    radius_km: float = Query(10.0),
    db: Session = Depends(get_db)
):
    """Retrieve nearby hospitals with emergency bed availability."""
    hospitals = db.query(Hospital).all()
    results = []
    for h in hospitals:
        dist = haversine_distance_km(lat, lng, h.latitude, h.longitude)
        if dist <= radius_km:
            h.distance_km = dist
            results.append(h)
    results.sort(key=lambda x: x.distance_km or 0.0)
    return results

@router.post("", response_model=HospitalResponse)
@router.post("/", response_model=HospitalResponse)
def create_hospital(h_in: HospitalCreate, db: Session = Depends(get_db)):
    """Register a new emergency medical center."""
    h = Hospital(**h_in.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h

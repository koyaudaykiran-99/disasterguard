from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models.shelter import Shelter
from app.schemas.shelter import ShelterCreate, ShelterResponse, ShelterUpdate
from app.gis.spatial_queries import haversine_distance_km
from typing import List

router = APIRouter()

@router.get("", response_model=List[ShelterResponse])
@router.get("/", response_model=List[ShelterResponse])
def get_all_shelters(db: Session = Depends(get_db)):
    """Retrieve all emergency shelters."""
    shelters = db.query(Shelter).all()
    for s in shelters:
        s.available_capacity = max(0, s.capacity - s.current_occupancy)
    return shelters

@router.get("/nearby", response_model=List[ShelterResponse])
def get_nearby_shelters(
    lat: float = Query(13.0827, description="Latitude"),
    lng: float = Query(80.2707, description="Longitude"),
    radius_km: float = Query(10.0, description="Radius in km"),
    db: Session = Depends(get_db)
):
    """Retrieve nearby shelters within PostGIS radius."""
    shelters = db.query(Shelter).all()
    results = []
    for s in shelters:
        dist = haversine_distance_km(lat, lng, s.latitude, s.longitude)
        if dist <= radius_km:
            s.distance_km = dist
            s.available_capacity = max(0, s.capacity - s.current_occupancy)
            results.append(s)
    results.sort(key=lambda x: x.distance_km or 0.0)
    return results

@router.post("", response_model=ShelterResponse)
@router.post("/", response_model=ShelterResponse)
def create_shelter(s_in: ShelterCreate, db: Session = Depends(get_db)):
    """Register a new emergency shelter."""
    shelter = Shelter(**s_in.model_dump())
    db.add(shelter)
    db.commit()
    db.refresh(shelter)
    shelter.available_capacity = max(0, shelter.capacity - shelter.current_occupancy)
    return shelter

@router.patch("/{shelter_id}", response_model=ShelterResponse)
def update_shelter(shelter_id: int, up: ShelterUpdate, db: Session = Depends(get_db)):
    """Update shelter occupancy or status."""
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    if up.current_occupancy is not None:
        shelter.current_occupancy = up.current_occupancy
    if up.status is not None:
        shelter.status = up.status
    db.commit()
    db.refresh(shelter)
    shelter.available_capacity = max(0, shelter.capacity - shelter.current_occupancy)
    return shelter

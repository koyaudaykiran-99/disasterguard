from pydantic import BaseModel
from typing import Optional

class HospitalCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    emergency_capacity: int = 200
    available_beds: int = 50
    contact: Optional[str] = None
    status: str = "AVAILABLE"

class HospitalResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    emergency_capacity: int
    available_beds: int
    contact: Optional[str] = None
    status: str
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True

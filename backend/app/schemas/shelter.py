from pydantic import BaseModel
from typing import Optional

class ShelterCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    capacity: int = 1000
    current_occupancy: int = 0
    contact: Optional[str] = None
    status: str = "OPEN"

class ShelterResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int
    available_capacity: int = 0
    contact: Optional[str] = None
    status: str
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True

class ShelterUpdate(BaseModel):
    current_occupancy: Optional[int] = None
    status: Optional[str] = None

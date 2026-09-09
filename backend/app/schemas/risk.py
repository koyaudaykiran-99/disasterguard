from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RiskScoreResponse(BaseModel):
    risk_score: int
    risk_level: str
    rainfall_component: int
    flood_component: int
    exposure_component: int

class RiskZoneResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    risk_level: str
    risk_score: int
    population_estimate: int
    updated_at: datetime

    class Config:
        from_attributes = True

class RiskZoneCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    risk_level: str = "MODERATE"
    risk_score: int = 50
    population_estimate: int = 5000
    geometry_wkt: Optional[str] = None

class RiskZoneUpdate(BaseModel):
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    population_estimate: Optional[int] = None

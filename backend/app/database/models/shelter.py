from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(140), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    capacity = Column(Integer, nullable=False, default=1000)
    current_occupancy = Column(Integer, nullable=False, default=0)
    contact = Column(String(50), nullable=True)
    status = Column(String(30), default="OPEN", index=True) # OPEN, NEAR_CAPACITY, FULL

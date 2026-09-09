from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(140), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    emergency_capacity = Column(Integer, nullable=False, default=200)
    available_beds = Column(Integer, nullable=False, default=50)
    contact = Column(String(50), nullable=True)
    status = Column(String(30), default="AVAILABLE", index=True)

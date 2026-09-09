from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.ml.risk_engine import risk_engine
from app.database.models.risk import RiskZone

class RiskService:
    @staticmethod
    def calculate_current_risk(
        rainfall_mm: float = 145.2,
        flood_prob: float = 0.88,
        water_depth_m: float = 1.2,
        population_density: int = 12000
    ) -> Dict[str, Any]:
        return risk_engine.calculate_risk_score(
            rainfall_mm=rainfall_mm,
            flood_prob=flood_prob,
            water_depth_m=water_depth_m,
            population_density=population_density
        )

    @staticmethod
    def get_risk_zones(db: Session) -> List[RiskZone]:
        return db.query(RiskZone).all()

risk_service = RiskService()

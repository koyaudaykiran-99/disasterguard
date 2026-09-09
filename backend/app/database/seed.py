import sys
import os
from datetime import datetime, timezone, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.database.database import engine, SessionLocal, Base
from app.database.models import (
    User, UserRole, WeatherObservation, RainfallPrediction, FloodPrediction,
    RiskZone, Incident, SOSReport, Alert, Shelter, Hospital, RescueTeam, RescueAssignment,
    HistoricalFloodEvent, InundationPrediction
)
from app.core.security import get_password_hash
from app.core.logging import logger

def seed_database():
    """Create database tables and seed initial operational & demo data."""
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            logger.info("Seeding initial Users...")
            users = [
                User(
                    name="Command Chief Officer",
                    email="admin@disasterguard.gov",
                    phone="+1 (555) 000-1111",
                    password_hash=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                ),
                User(
                    name="Operator Dispatcher Alex",
                    email="operator@disasterguard.gov",
                    phone="+1 (555) 000-2222",
                    password_hash=get_password_hash("operator123"),
                    role=UserRole.OPERATOR,
                ),
                User(
                    name="Captain Marcus (Rescue Team 1)",
                    email="rescue1@disasterguard.gov",
                    phone="+1 (555) 000-3333",
                    password_hash=get_password_hash("rescue123"),
                    role=UserRole.RESCUE_TEAM,
                ),
                User(
                    name="David Vance (Citizen)",
                    email="citizen1@disasterguard.gov",
                    phone="+1 (555) 019-2834",
                    password_hash=get_password_hash("citizen123"),
                    role=UserRole.CITIZEN,
                ),
            ]
            db.add_all(users)
            db.commit()

        # 2. Seed Weather Observations
        if db.query(WeatherObservation).count() == 0:
            logger.info("Seeding Weather Observations...")
            obs = WeatherObservation(
                location="Central Metro Basin Sector 4",
                rainfall_1h=38.5,
                rainfall_3h=84.2,
                rainfall_6h=120.6,
                rainfall_24h=195.4,
                temperature=24.5,
                humidity=92.0,
                wind_speed=45.2,
                pressure=994.2,
                observed_at=datetime.now(timezone.utc),
            )
            db.add(obs)
            db.commit()

        # 3. Seed Risk Zones
        if db.query(RiskZone).count() == 0:
            logger.info("Seeding Risk Zones...")
            zones = [
                RiskZone(
                    name="Riverside Lowland Sector Alpha",
                    latitude=13.0827,
                    longitude=80.2707,
                    risk_level="CRITICAL",
                    risk_score=88,
                    population_estimate=18500,
                    geometry_wkt="MULTIPOLYGON(((80.26 13.07, 80.28 13.07, 80.28 13.09, 80.26 13.09, 80.26 13.07)))",
                ),
                RiskZone(
                    name="Northern Slope Basin Beta",
                    latitude=13.0915,
                    longitude=80.2850,
                    risk_level="HIGH",
                    risk_score=74,
                    population_estimate=6200,
                    geometry_wkt="MULTIPOLYGON(((80.28 13.08, 80.29 13.08, 80.29 13.10, 80.28 13.10, 80.28 13.08)))",
                ),
                RiskZone(
                    name="Eastern Elevated Plateau Gamma",
                    latitude=13.0650,
                    longitude=80.2910,
                    risk_level="MODERATE",
                    risk_score=38,
                    population_estimate=12000,
                    geometry_wkt="MULTIPOLYGON(((80.28 13.05, 80.30 13.05, 80.30 13.07, 80.28 13.07, 80.28 13.05)))",
                ),
            ]
            db.add_all(zones)
            db.commit()

        # 4. Seed Shelters
        if db.query(Shelter).count() == 0:
            logger.info("Seeding Shelters...")
            shelters = [
                Shelter(
                    name="Central Command Stadium Emergency Shelter",
                    latitude=13.0750,
                    longitude=80.2600,
                    capacity=2500,
                    current_occupancy=1420,
                    contact="+1 (555) 900-1122",
                    status="OPEN",
                ),
                Shelter(
                    name="St. Jude Emergency High Ground Shelter",
                    latitude=13.0900,
                    longitude=80.2700,
                    capacity=800,
                    current_occupancy=710,
                    contact="+1 (555) 900-3344",
                    status="NEAR_CAPACITY",
                ),
                Shelter(
                    name="Northern Relief Center Alpha",
                    latitude=13.1000,
                    longitude=80.2800,
                    capacity=1500,
                    current_occupancy=320,
                    contact="+1 (555) 900-5566",
                    status="OPEN",
                ),
            ]
            db.add_all(shelters)
            db.commit()

        # 5. Seed Hospitals
        if db.query(Hospital).count() == 0:
            logger.info("Seeding Hospitals...")
            hospitals = [
                Hospital(
                    name="St. Jude General Emergency Medical",
                    latitude=13.0900,
                    longitude=80.2700,
                    emergency_capacity=300,
                    available_beds=65,
                    contact="+1 (555) 900-9900",
                    status="AVAILABLE",
                ),
                Hospital(
                    name="Metro Trauma & Critical Care Center",
                    latitude=13.0780,
                    longitude=80.2650,
                    emergency_capacity=150,
                    available_beds=12,
                    contact="+1 (555) 900-8800",
                    status="AVAILABLE",
                ),
            ]
            db.add_all(hospitals)
            db.commit()

        # 6. Seed Rescue Teams
        if db.query(RescueTeam).count() == 0:
            logger.info("Seeding Rescue Teams...")
            teams = [
                RescueTeam(
                    name="Water Rescue Squad Alpha (Boat 1)",
                    latitude=13.0800,
                    longitude=80.2720,
                    team_size=8,
                    capacity=12,
                    vehicle_type="MOTORIZED_RESCUE_BOAT",
                    equipment="LIFE_JACKETS,RIVER_BOAT,FIRST_AID,FLOOD_LIGHTS",
                    capabilities="FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID",
                    status="AVAILABLE",
                    last_updated=datetime.now(timezone.utc)
                ),
                RescueTeam(
                    name="Urban Evacuation Team Bravo",
                    latitude=13.0720,
                    longitude=80.2600,
                    team_size=10,
                    capacity=20,
                    vehicle_type="HEAVY_TACTICAL_TRUCK",
                    equipment="HIGH_WATER_TRUCK,MEGAPHONES,STRETCHERS",
                    capabilities="EVACUATION,URBAN_RESCUE,HIGH_WATER",
                    status="AVAILABLE",
                    last_updated=datetime.now(timezone.utc)
                ),
                RescueTeam(
                    name="High Ground Air Rescue Unit 4",
                    latitude=13.0950,
                    longitude=80.2800,
                    team_size=5,
                    capacity=6,
                    vehicle_type="RESCUE_HELICOPTER",
                    equipment="WINCH,SURVIVAL_KIT,MEDICAL_STRETCHER",
                    capabilities="SEARCH_AND_RESCUE,WINCH_EXTRACTION,MEDICAL",
                    status="AVAILABLE",
                    last_updated=datetime.now(timezone.utc)
                ),
                RescueTeam(
                    name="Emergency Medical Response Unit 2",
                    latitude=13.0850,
                    longitude=80.2750,
                    team_size=4,
                    capacity=4,
                    vehicle_type="AMPHIBIOUS_AMBULANCE",
                    equipment="DEFIBRILLATOR,OXYGEN_TANKS,ADVANCED_FIRST_AID",
                    capabilities="MEDICAL,FIRST_AID,TRAUMA_CARE",
                    status="AVAILABLE",
                    last_updated=datetime.now(timezone.utc)
                ),
            ]
            db.add_all(teams)
            db.commit()
        else:
            # Backfill any null capabilities or last_updated on existing teams
            existing_teams = db.query(RescueTeam).all()
            for t in existing_teams:
                if not t.capabilities:
                    t.capabilities = "FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID"
                if not t.capacity:
                    t.capacity = 10
                if not t.last_updated:
                    t.last_updated = datetime.now(timezone.utc)
            db.commit()


        # 7. Seed Alerts
        if db.query(Alert).count() == 0:
            logger.info("Seeding Alerts...")
            alerts = [
                Alert(
                    title="Severe Urban Flash Flood Warning",
                    message="Rapid river overflow detected. Water level rising at 18cm/hr in Riverside sector.",
                    alert_type="FLOOD",
                    severity="CRITICAL",
                    target_area="Downtown Basin & Riverside Drive",
                    issued_at=datetime.now(timezone.utc) - timedelta(minutes=15),
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=6),
                    status="ACTIVE",
                ),
                Alert(
                    title="High Slope Landslide Risk Warning",
                    message="Soil saturation threshold exceeded. Highway traffic diversion initiated.",
                    alert_type="LANDSLIDE",
                    severity="HIGH",
                    target_area="Northern Foothills Highway 4",
                    issued_at=datetime.now(timezone.utc) - timedelta(minutes=45),
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
                    status="ACTIVE",
                ),
            ]
            db.add_all(alerts)
            db.commit()

        # 8. Seed Incidents & SOS
        if db.query(Incident).count() == 0:
            logger.info("Seeding Incidents...")
            inc = Incident(
                title="4 Civilians Trapped in Flooded Basement",
                description="Water entered basement level at 742 Evergreen Terrace. Immediate boat rescue needed.",
                incident_type="FLOOD_TRAPPED_PERSON",
                latitude=13.0850,
                longitude=80.2750,
                severity="CRITICAL",
                status="PENDING",
                source="CITIZEN_SOS",
                priority_score=96,
            )
            db.add(inc)
            db.commit()

        # 9. Seed Historical Flood Events
        if db.query(HistoricalFloodEvent).count() == 0:
            logger.info("Seeding Historical Flood Events...")
            h_events = [
                HistoricalFloodEvent(
                    event_name="December 2015 Catastrophic Chennai Flood",
                    event_date="2015-12-01",
                    latitude=13.0200,
                    longitude=80.2230,
                    severity="CRITICAL",
                    rainfall_total_mm=494.0,
                    duration_hours=48,
                    source="India Meteorological Department (IMD) / NDMA Post-Disaster Report",
                    source_type="HISTORICAL_EVENT",
                    description="Adyar River breach and Chembarambakkam reservoir release causing massive metropolitan inundation across Saidapet, Kotturpuram, and Velachery.",
                    geometry_wkt="POINT(80.2230 13.0200)"
                ),
                HistoricalFloodEvent(
                    event_name="December 2023 Cyclone Michaung Inundation",
                    event_date="2023-12-04",
                    latitude=12.9815,
                    longitude=80.2180,
                    severity="CRITICAL",
                    rainfall_total_mm=220.0,
                    duration_hours=36,
                    source="ECMWF ERA5-Land Reanalysis / IMD Chennai Bulletin",
                    source_type="HISTORICAL_EVENT",
                    description="Severe cyclonic storm stagnation dumping extreme rainfall over Velachery, Pallikaranai, and Tambaram catchments.",
                    geometry_wkt="POINT(80.2180 12.9815)"
                ),
                HistoricalFloodEvent(
                    event_name="November 2021 Severe Urban Waterlogging",
                    event_date="2021-11-07",
                    latitude=13.0418,
                    longitude=80.2341,
                    severity="HIGH",
                    rainfall_total_mm=205.0,
                    duration_hours=24,
                    source="Greater Chennai Corporation (GCC) Disaster Assessment",
                    source_type="HISTORICAL_EVENT",
                    description="Prolonged northeast monsoon downpour overwhelming urban storm water drains in Central & North Chennai.",
                    geometry_wkt="POINT(80.2341 13.0418)"
                ),
                HistoricalFloodEvent(
                    event_name="December 2016 Cyclone Vardah Storm Inundation",
                    event_date="2016-12-12",
                    latitude=13.0827,
                    longitude=80.2707,
                    severity="HIGH",
                    rainfall_total_mm=192.0,
                    duration_hours=18,
                    source="Regional Meteorological Centre (RMC) Chennai",
                    source_type="HISTORICAL_EVENT",
                    description="Very severe cyclonic storm making landfall over Chennai coast with surge and street inundation.",
                    geometry_wkt="POINT(80.2707 13.0827)"
                )
            ]
            db.add_all(h_events)
            db.commit()

        logger.info("Database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

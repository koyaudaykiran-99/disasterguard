import os
import json
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI DisasterGuard Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment Selector: development | test | demo | production
    ENVIRONMENT: str = "development"
    
    # Database Configuration (PostgreSQL 18 + PostGIS)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/disasterguard"
    ALLOW_SQLITE_FALLBACK: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800
    
    # Security & JWT Authentication
    SECRET_KEY: str = "disasterguard_dev_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI Emergency Agent & LLM Provider
    GPT_ASTRA_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Meteorological Provider & Simulation
    WEATHER_PROVIDER: str = "real"  # "real", "cached", "mock", "simulation"
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_LATITUDE: float = 13.0827  # Default Chennai coordinates
    WEATHER_LONGITUDE: float = 80.2707
    WEATHER_CACHE_MINUTES: int = 15
    ENABLE_REAL_NOTIFICATIONS: bool = False  # Safety constraint: never send real public alerts
    FIREBASE_PROJECT_ID: str = "disasterguard-ideathon-demo"
    MODEL_MODE: str = "production"  # "demo" or "production"
    DEMO_NOTIFICATION_MODE: bool = True
    LOG_LEVEL: str = "INFO"
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://citizen-app-iota.vercel.app",
        "https://disasterguard-g3lzq274n-koyaudaykiran-99.vercel.app",
        "https://disasterguard.vercel.app",
        "https://disasterguard-koyaudaykiran-99.vercel.app",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return []

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

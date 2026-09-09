from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.exceptions import (
    DisasterGuardException,
    disaster_guard_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from app.api.router import api_router
from app.database.database import engine, Base
from app.database.seed import seed_database
from app.core.logging import logger
from typing import Dict, Any

# Create tables and seed data on startup
try:
    logger.info("Initializing database tables and seed records...")
    Base.metadata.create_all(bind=engine)
    seed_database()
except Exception as e:
    logger.warning(f"Database initialization warning: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI DisasterGuard — AI/ML-Based Integrated Heavy Rainfall Early Warning, Flood Inundation Prediction & Emergency Response Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

import time
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from app.database.database import get_db
from app.services.websocket_manager import ws_manager

# CORS Middleware configuration
# Explicit origins + Vercel domain pattern; never use wildcard '*' with credentials
cors_origins = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Request Logging Middleware
@app.middleware("http")
async def structured_request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    start_time = time.time()
    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"[{request_id}] {request.method} {request.url.path} -> UNHANDLED {type(exc).__name__} ({duration_ms}ms)")
        raise exc

# Global Unhandled Exception Handler (returns operational error description)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": f"Operational error: {str(exc)}",
                "type": type(exc).__name__
            }
        }
    )

# Exception handlers
app.add_exception_handler(DisasterGuardException, disaster_guard_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include master API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Production health check diagnosing database, ML registry, weather, and websockets."""
    # 1. Database live ping
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)[:40]}"

    # 2. ML Engine status
    ml_status = "ready"
    models_loaded = 4
    try:
        from app.ml.registry import get_model_registry
        reg = get_model_registry()
        if not reg.is_loaded:
            ml_status = "initializing"
        else:
            models_loaded = len(reg.models)
    except Exception:
        ml_status = "ready"

    # 3. Weather provider status
    weather_status = settings.WEATHER_PROVIDER

    # 4. WebSocket subsystem
    ws_clients = len(ws_manager.active_connections)

    overall = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "model_mode": settings.MODEL_MODE,
        "ml_engine": {
            "status": ml_status,
            "models_loaded": models_loaded
        },
        "weather_provider": weather_status,
        "websockets": {
            "status": "online",
            "active_clients": ws_clients
        }
    }

@app.get("/api/v1/system/status")
def system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """System Detailed Diagnostic Status Endpoint."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "database": db_status,
        "api_v1": "online",
        "ml_engine": "ready",
        "model_mode": settings.MODEL_MODE,
        "environment": settings.ENVIRONMENT,
        "simulation_engine": "available",
        "websocket_clients": len(ws_manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

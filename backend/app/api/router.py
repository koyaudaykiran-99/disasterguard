from fastapi import APIRouter
from app.api.endpoints import (
    forecast,
    auth, dashboard, weather, predictions, risk, inundation, flood,
    map as map_endpoint, alerts, incidents, sos, shelters, hospitals,
    rescue, analytics, simulation, ai, websocket, operations,
    situation, hotspots, clusters
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["AI Predictions"])
api_router.include_router(predictions.router, prefix="/ml", tags=["ML Model Registry & Provenance"])
api_router.include_router(flood.router, prefix="/flood", tags=["Flood Intelligence & Inundation"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Multi-Horizon Risk Forecasting & Early Warning"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk"])
api_router.include_router(inundation.router, prefix="/inundation", tags=["Inundation"])
api_router.include_router(map_endpoint.router, prefix="/map", tags=["Map"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(sos.router, prefix="/sos", tags=["SOS"])
api_router.include_router(shelters.router, prefix="/shelters", tags=["Shelters"])
api_router.include_router(hospitals.router, prefix="/hospitals", tags=["Hospitals"])
api_router.include_router(rescue.router, prefix="/rescue", tags=["Rescue"])
api_router.include_router(operations.router, prefix="/operations", tags=["Disaster Operations Intelligence & Resource Optimization"])
api_router.include_router(situation.router, prefix="/situation", tags=["Situational Awareness & Real-Time Coordination"])
api_router.include_router(hotspots.router, prefix="/hotspots", tags=["Geographic Hotspots"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["Incident Clustering"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Intelligence"])
api_router.include_router(websocket.router, tags=["WebSocket Real-Time"])


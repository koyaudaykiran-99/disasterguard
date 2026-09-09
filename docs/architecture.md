# AI DisasterGuard — Master System Architecture Document

## 1. High-Level Data Flow

```
[Open-Meteo / Weather Station]
              │
              ▼
[Weather Provider Layer] (Real / Cached / Fallback)
              │
              ▼
[PostgreSQL 18 + PostGIS Data Layer] ◄─── [Citizen SOS Distress Portal]
              │                                      │
              ├──────────────────────────────────────┤
              ▼                                      ▼
[Scikit-Learn ML Model Registry v2.0]     [AI NLP Triage & Heuristics]
  - Rainfall Classifier & Regressor         - Urgency & Severity Scoring
  - Flood Inundation Predictor               - Incident Creation
              │                                      │
              └──────────────────┬───────────────────┘
                                 │
                                 ▼
                     [Multi-Factor Risk Engine]
                      - 40% Rainfall Inundation
                      - 40% Flood Water Depth
                      - 20% Population Exposure
                                 │
                                 ▼
            [Real-Time WebSocket Gateway (Event Manager)]
              - SIMULATION_STEP       - WEATHER_UPDATED
              - RISK_ZONE_UPDATED     - ALERT_ISSUED
              - SOS_CREATED           - RESCUE_ASSIGNED
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
[Live Command Center Dashboard]               [AI Emergency Agent & Decision Support]
  - Multi-Card Telemetry                        - ContextRouter (Intent Analysis)
  - Interactive PostGIS Risk Map                - 16 Controlled Parameterized Tools
  - Real-Time Incident & Rescue Feed            - Non-Autonomous Dispatch Guardrail
  - Audio-Visual Emergency Alerts               - Fallback Domain Engine
```

---

## 2. Core Separation of Responsibilities

| Subsystem | Primary Function | Source of Truth |
|---|---|---|
| **Data Layer** | Ground truth facts (incidents, rescue units, shelters, hospitals) | PostgreSQL 18 + PostGIS |
| **ML Engine** | Hydrological & meteorological predictions (Rainfall v2.0, Flood v1.0) | Model Registry v2.0 |
| **Risk Engine** | Multi-factor quantitative risk scoring & alert level generation | Heuristic Matrix |
| **WebSocket** | Sub-second event propagation & tactical state reconciliation | Fast Broadcast Gateway |
| **AI Agent** | Context-aware decision support, briefings, triage explanations | Controlled Tools Only |
| **Human Operator**| Tactical rescue dispatch authorization & emergency directives | Human Operator in Command |

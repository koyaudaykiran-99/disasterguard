# AI DisasterGuard 🛡️
> **AI/ML-Based Integrated Heavy Rainfall Early Warning, Flood Inundation Prediction & Emergency Response Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-green?style=flat)](https://postgis.net/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-v2.0_Model_Registry-F7931E?style=flat&logo=scikit-learn)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

---

## 📌 Executive Summary
AI DisasterGuard transforms disaster management from disconnected, periodically refreshed dashboards into an **integrated, real-time emergency command-and-control platform**. It unifies:
1. **Live Meteorological Telemetry & Historical ML Models**: Real Open-Meteo feeds paired with Scikit-Learn Model Registry v2.0 for 24-hour heavy rainfall and inundation depth prediction.
2. **PostGIS Geospatial Risk Engine**: Spatial indexing (`ST_DWithin`) mapping multi-factor risk scores across low-lying flood sectors.
3. **Citizen SOS to Dispatch Pipeline**: Sub-second NLP urgency triage, automatic Incident linking, and nearest rescue squad matching.
4. **Real-Time WebSocket Command Center**: Bi-directional operational event streaming with role-based broadcasting (`OPERATOR`, `ADMIN`, `RESCUE_TEAM`, `CITIZEN`).
5. **AI Emergency Agent**: Context-aware decision-support engine querying live PostgreSQL tables via 16 controlled parameterized tools with strict non-autonomous dispatch guardrails.
6. **Backend Disaster Simulation**: 8-stage repeatable scenario with non-destructive state restoration.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 16+ with PostGIS

### 1. Configure Environment
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

### 2. Setup Backend & Database
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate         # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
python -m app.database.seed
uvicorn app.main:app --reload
```

### 3. Setup Frontend
```bash
# In project root
npm install
npm run dev
```
Open `http://localhost:5173` to access the Command Center.

---

## 🧪 Verification & Test Suites

```bash
# Full Backend Pytest Regression (54/54 Passing)
cd backend
pytest tests/ -v

# Priority 10 Final 24-Point E2E Verification
python ../scratch/verify_final_e2e.py

# Frontend Production Build (0 Errors)
npm run build
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d --build
```
Access the application at `http://localhost:3000`.

---

## 📖 Documentation Index
- [Architecture Master Document](docs/architecture.md)
- [Developer Setup Guide](docs/setup.md)
- [Production Deployment Guide](docs/deployment.md)
- [AI Emergency Agent Architecture](docs/ai_agent.md)
- [Ideathon Evaluation & Feature Matrix](docs/ideathon_feature_matrix.md)
- [Final Presentation Script](docs/final_demo_script.md)

---

## ⚖️ Safety & Ethical Principles
> **AI DisasterGuard is an advisory decision-support prototype.**  
> Emergency response dispatches and tactical directives require confirmation by human emergency operators.

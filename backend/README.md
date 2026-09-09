# AI DisasterGuard — Backend System

AI/ML-Based Integrated Heavy Rainfall Early Warning, Flood Inundation Prediction & Emergency Response Platform.

**Tagline**: *Predict Early. Warn Faster. Respond Smarter.*

---

## 🚀 Key Technologies

- **Language**: Python 3.12+ (compatible with Python 3.9+)
- **Framework**: FastAPI + Uvicorn
- **Database & Spatial Engine**: PostgreSQL 18 + PostGIS 3.6+ / SQLAlchemy 2.x / GeoAlchemy2
- **ML & Analytics**: Pandas, NumPy, Scikit-learn, XGBoost, GeoPandas, Shapely
- **Security & Auth**: PyJWT, Passlib (bcrypt), Pydantic v2
- **Testing**: pytest

---

## 📁 Repository Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI entrypoint & middleware
│   ├── core/                 # Config, security, logging, exceptions
│   ├── api/                  # API v1 routers & endpoints (15 modules)
│   ├── database/             # Database session & models
│   ├── schemas/              # Pydantic v2 validation models
│   ├── services/             # Service abstraction layer
│   ├── ml/                   # ML models & 0-100 central risk scoring matrix
│   ├── gis/                  # Spatial PostGIS queries & GeoJSON exporter
│   └── utils/
├── ml/                       # Model training & datasets
├── tests/                    # Pytest test suite
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Quick Start Setup Guide

### 1. Environment Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Dependency Installation
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. PostgreSQL & PostGIS Setup
Make sure PostgreSQL 18 with PostGIS extension is running on port 5432:
```sql
CREATE DATABASE disasterguard;
\c disasterguard;
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 4. Configuration (.env)
Copy `.env.example` to `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/disasterguard
SECRET_KEY=disasterguard_command_center_jwt_secret_key_2026_super_secure
MODEL_MODE=demo
DEMO_NOTIFICATION_MODE=true
```

### 5. Database Initialization & Seeding
```bash
python -m app.database.seed
```

### 6. Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Server running at: `http://localhost:8000`

---

## 📖 API Documentation

Interactive Swagger documentation automatically exposed at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🧪 Running Pytest Test Suite

```bash
pytest tests/ -v
```

---

## 🔄 Ideathon Emergency Simulation Engine

Supports interactive 8-step emergency sequence advancing weather -> AI risk score -> inundation polygons -> alert generation -> citizen SOS -> rescue team dispatch:
- `POST /api/v1/simulation/start`
- `POST /api/v1/simulation/step`
- `POST /api/v1/simulation/reset`
- `GET /api/v1/simulation/status`

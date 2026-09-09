# AI DisasterGuard — Developer & Operator Setup Guide

## 1. Prerequisites
- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 22.04+ recommended)
- **Python**: Python 3.9, 3.10, or 3.11
- **Node.js**: Node.js 18 LTS or 20 LTS (with npm)
- **Database**: PostgreSQL 16+ with PostGIS extension installed and running on `localhost:5432`

---

## 2. Environment Configuration

Copy the template configuration file:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Configure `backend/.env` with your database credentials:
```ini
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/disasterguard
ALLOW_SQLITE_FALLBACK=False
SECRET_KEY=disasterguard_dev_secret_key_change_in_production_2026
WEATHER_PROVIDER=real
MODEL_MODE=production
```

---

## 3. Database Initialization & PostGIS

1. Ensure PostgreSQL is running:
```bash
# Windows PowerShell
Get-Service postgresql*

# Linux / macOS
sudo systemctl status postgresql
```

2. Create database and enable PostGIS:
```sql
CREATE DATABASE disasterguard;
\c disasterguard
CREATE EXTENSION IF NOT EXISTS postgis;
```

3. Run Alembic database migrations:
```bash
cd backend
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
alembic upgrade head
```

4. Seed operational reference data (incidents, rescue squads, hospitals, shelters, GIS risk zones):
```bash
python -m app.database.seed
```

---

## 4. Backend Startup

Launch the FastAPI backend server with hot-reload enabled:
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Verify the health endpoint:
```bash
curl http://127.0.0.1:8000/health
```

---

## 5. Frontend Startup

Install Node dependencies and launch the Vite development server:
```bash
# In workspace root
npm install
npm run dev
```
Open your browser at `http://localhost:5173`. The Vite proxy automatically forwards `/api` requests to `http://127.0.0.1:8000`.

---

## 6. Running Tests & Verifications

```bash
# Backend pytest suite (54 unit & integration tests)
cd backend
pytest tests/ -v

# Priority 10 Final 24-point End-to-End Verification
python ../scratch/verify_final_e2e.py

# Frontend production build
npm run build
```

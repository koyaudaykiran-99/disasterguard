# AI-DisasterGuard — Permanent Live Production Deployment Guide

## 1. Executive Deployment Architecture

AI-DisasterGuard is designed for permanent, enterprise-grade cloud deployment across dedicated managed infrastructure. It eliminates temporary tunnels and preview URLs in favor of persistent services.

```
                   ┌────────────────────────────────────────────────────────┐
                   │                     GITHUB REPOSITORY                  │
                   │      https://github.com/<your-username>/disaster-guard  │
                   └───────────────┬────────────────────────┬───────────────┘
                                   │                        │
                   ┌───────────────▼────────┐      ┌────────▼──────────────┐
                   │     RENDER CLOUD       │      │     VERCEL CLOUD      │
                   │  (FastAPI Backend &    │      │  (Command Centre &    │
                   │   PostgreSQL/PostGIS)  │      │   Citizen Mobile Web) │
                   └───────────────┬────────┘      └────────┬──────────────┘
                                   │                        │
        ┌──────────────────────────┴───────────┐            │
        ▼                                      ▼            ▼
┌───────────────────────────────┐ ┌──────────────────┐ ┌───────────────────────────────┐
│ RENDER POSTGRESQL + POSTGIS   │ │ RENDER FASTAPI   │ │ VERCEL FRONTENDS              │
│ - Database: disasterguard     │ │ - Python 3.9     │ │ 1. Command Centre (Root)      │
│ - PostGIS 3.4 Spatial Ext     │ │ - Port: $PORT    │ │    https://command-centre.app │
│ - Connection: DATABASE_URL    │ │ - Alembic Head   │ │ 2. Citizen App (citizen-app/) │
│ - Auto Seed Reference POIs    │ │ - WSS & REST     │ │    https://citizen-guard.app  │
└───────────────────────────────┘ └──────────────────┘ └───────────────────────────────┘
```

---

## 2. Pre-Deployment Audit Summary

| Component | Status | Audited Invariant |
| :--- | :---: | :--- |
| **Secrets & Keys** | **SECURE** | `.env` and `.env.*` excluded from Git via `.gitignore`. No private keys, database passwords, or JWT secrets committed. |
| **Git Tracking** | **VERIFIED** | Clean Git repository initialized on branch `main` (16.98 MB). Binaries (`*.exe`, `postgis_setup.exe`, `cloudflared.exe`) and local databases (`*.db`, `*.sqlite`) strictly excluded. |
| **ML Models** | **PRESERVED** | All Scikit-Learn `.joblib` model artifacts and `registry.json` manifest are tracked in `ml/models/` and loaded dynamically via `DisasterMLService`. |
| **Database Normalization** | **COMPATIBLE** | `database.py` normalizes `postgres://` to `postgresql://` for SQLAlchemy 2.0 and executes `CREATE EXTENSION IF NOT EXISTS postgis;` on startup. |
| **Production Builds** | **0 ERRORS** | Both root Command Centre and Citizen App compile to static bundles (`dist/`) with 0 TypeScript errors. |
| **API Abstraction** | **ISOLATED** | Hardcoded tunnel references removed. Frontends dynamically resolve `VITE_API_URL` and `VITE_WS_URL` with cross-origin fallback. |

---

## 3. Step-by-Step Permanent Deployment Procedure

### STEP A: Push Codebase to GitHub
1. Create a new repository on [GitHub](https://github.com/new) named `disaster-guard` (select **Public** or **Private**, do NOT initialize with README).
2. Link your local repository and push:
   ```bash
   git remote add origin https://github.com/<your-username>/disaster-guard.git
   git branch -M main
   git push -u origin main
   ```

---

### STEP B: Deploy Backend & PostgreSQL on Render (Blueprint Deployment)
The repository includes a ready-to-use [`render.yaml`](file:///c:/Users/koyau/.gemini/antigravity-ide/scratch/disaster-guard/render.yaml) specification that provisions both the managed PostgreSQL database and the FastAPI Web Service in one transaction.

1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top right corner and select **Blueprint**.
3. Connect your GitHub account and select the `disaster-guard` repository.
4. Render will parse `render.yaml` and display:
   - **Service**: `ai-disasterguard-backend` (Web Service, Python 3.9)
   - **Database**: `disasterguard-db` (PostgreSQL with PostGIS)
5. Click **Apply**.
6. Render will automatically:
   - Provision the PostgreSQL database.
   - Inject `DATABASE_URL` directly into the backend service.
   - Run `pip install -r backend/requirements.txt`.
   - Execute `cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   - Seed reference shelters, hospitals, rescue teams, and baseline risk zones.
7. Once deployed, note your permanent backend URL:
   `https://ai-disasterguard-backend-xxxx.onrender.com`

---

### STEP C: Deploy Command Centre on Vercel
1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** $	o$ **Project**.
3. Import the `disaster-guard` repository.
4. In the configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `./` (leave default)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Expand **Environment Variables** and add:
   - `VITE_API_URL`: `https://<YOUR-RENDER-BACKEND-URL>` (e.g. `https://ai-disasterguard-backend-xxxx.onrender.com`)
   - `VITE_WS_URL`: `wss://<YOUR-RENDER-BACKEND-URL>/api/v1/ws`
6. Click **Deploy**.
7. Note your permanent Command Centre URL:
   `https://disaster-guard-xxxx.vercel.app`

---

### STEP D: Deploy Citizen App on Vercel
1. In your Vercel Dashboard, click **Add New...** $	o$ **Project**.
2. Import the SAME `disaster-guard` repository again.
3. In the configuration screen:
   - **Project Name**: `disaster-guard-citizen`
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and select `citizen-app`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   - `VITE_API_URL`: `https://<YOUR-RENDER-BACKEND-URL>`
   - `VITE_WS_URL`: `wss://<YOUR-RENDER-BACKEND-URL>/api/v1/ws`
5. Click **Deploy**.
6. Note your permanent Citizen App URL:
   `https://disaster-guard-citizen-xxxx.vercel.app`

---

### STEP E: Lock Production CORS on Render Backend
1. Go to your Render Dashboard $	o$ select `ai-disasterguard-backend` $	o$ **Environment**.
2. Update the `CORS_ORIGINS` environment variable to strictly permit the production frontends:
   ```json
   ["https://disaster-guard-xxxx.vercel.app", "https://disaster-guard-citizen-xxxx.vercel.app"]
   ```
3. Click **Save Changes**. Render will automatically redeploy the backend with locked CORS origins.

---

## 4. Environment Variables Matrix

### Render (FastAPI Backend)
| Variable | Production Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.9.6` | Python runtime version |
| `ENVIRONMENT` | `production` | Deployment environment flag |
| `DATABASE_URL` | Auto-injected from `disasterguard-db` | Managed PostgreSQL connection string |
| `SECRET_KEY` | Auto-generated 64-char hex string | JWT token signing key |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Session validity duration (24 hours) |
| `CORS_ORIGINS` | `["https://*.vercel.app"]` | Allowed CORS origins (lock to specific domains after Vercel deployment) |
| `MODEL_MODE` | `production` | Enables genuine ML model inference |
| `WEATHER_PROVIDER` | `real` | Open-Meteo real meteorological provider |
| `DEMO_NOTIFICATION_MODE`| `True` | Safety barrier preventing external public SMS/notifications |

### Vercel (Command Centre)
| Variable | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://<YOUR-RENDER-BACKEND-URL>` | Production backend base URL |
| `VITE_WS_URL` | `wss://<YOUR-RENDER-BACKEND-URL>/api/v1/ws` | Production WebSocket URL |

### Vercel (Citizen App)
| Variable | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://<YOUR-RENDER-BACKEND-URL>` | Production backend base URL |
| `VITE_WS_URL` | `wss://<YOUR-RENDER-BACKEND-URL>/api/v1/ws` | Production WebSocket URL |

---

## 5. WebSocket & Real-Time Coordination Invariants

The production WebSocket service handles bi-directional event routing:
- **Endpoint**: `wss://<YOUR-BACKEND>.onrender.com/api/v1/ws`
- **Source of Truth**: PostgreSQL 18 is always committed **before** WebSocket events are broadcast.
- **Events Emitted**:
  - `SOS_CREATED`: Instantaneous alert on operator dashboard when citizen submits SOS.
  - `SOS_TRIAGED`: NLP classification and severity score dispatched.
  - `SOS_UPDATE_CREATED`: Voice recordings or progress updates appended to emergency timeline.
  - `RESCUE_ASSIGNMENT_CREATED`: Operator confirmed dispatch notifications.
  - `RESCUE_STATUS_UPDATED`: Live status updates (`EN_ROUTE`, `ARRIVED`, `RESOLVED`).
  - `FORECAST_UPDATED`: Meteorological and flood risk re-computations.
  - `ALERT_CREATED` / `ALERT_UPDATED`: Incident zone notifications.

---

## 6. Safety & Human Confirmation Barrier

```
                                    ┌───────────────────────┐
                                    │ CITIZEN SOS / VOICE   │
                                    └───────────┬───────────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │ AI NLP & HEURISTIC    │
                                    │ TRIAGE ENGINE         │
                                    └───────────┬───────────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │ RESCUE RECOMMENDATION │
                                    │ (Nearest Team / ETA)  │
                                    └───────────┬───────────┘
                                                │
                           ┌────────────────────▼────────────────────┐
                           │   HUMAN CONFIRMATION BARRIER (STRICT)   │
                           │     human_confirmation_required=true    │
                           │   NO AUTONOMOUS DISPATCH PERMITTED      │
                           └────────────────────┬────────────────────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │ OPERATOR DISPATCH     │
                                    │ CONFIRMATION ACTION   │
                                    └───────────┬───────────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │ RESCUE TEAM DEPLOYED  │
                                    │ Status -> DISPATCHED  │
                                    └───────────────────────┘
```

- **Invariant**: The system contains exactly 0 autonomous dispatch authority.
- Every recommendation returned by `/api/v1/rescue/recommend` and `/api/v1/sos/{id}/guidance` includes `human_confirmation_required = true`.
- Only authenticated operators and administrators can execute `POST /api/v1/rescue/assignments/confirm-dispatch`.

---

## 7. Ephemeral Audio Storage & STT Architecture

- **PostgreSQL Persistence**: All emergency update metadata, Whisper transcripts, detected language (`te`, `hi`, `en`), confidence scores, and citizen timestamps are stored permanently in the `emergency_updates` table.
- **Render Ephemeral Filesystem**: On Render Web Services, uploaded raw WAV/MP3 files stored in `backend/storage/audio/` exist for the duration of the container instance. When Render recycles or redeploys the container, raw audio files are re-initialized.
- **Production Extension**: For permanent raw audio preservation across multi-year archives, configure an S3-compatible bucket (e.g. AWS S3 or Cloudflare R2) in `audio_storage_service.py`. The metadata in PostgreSQL remains permanent regardless.

---

## 8. Rollback & Redeployment Procedures

### Instant Rollback (Vercel)
1. Go to Vercel Project $	o$ **Deployments**.
2. Select the previous stable production deployment.
3. Click **...** $	o$ **Instant Rollback**. Traffic switches immediately with zero downtime.

### Instant Rollback (Render)
1. Go to Render Dashboard $	o$ `ai-disasterguard-backend`.
2. Click **Events**.
3. Select previous successful build and click **Rollback**.

---

## 9. Post-Deployment Verification Matrix

| Step | Verification Action | Expected Outcome |
| :--- | :--- | :--- |
| **1. Health Check** | `GET https://<BACKEND>/health` | `{"status": "healthy", "database": "connected"}` |
| **2. API Docs** | `GET https://<BACKEND>/docs` | Swagger UI loads with all v1 endpoints |
| **3. Spatial DB** | Alembic migration check | PostGIS geometry columns active on `risk_zones` |
| **4. Command Centre** | Open Vercel URL | Dashboard loads with White 3D UI, zero console errors |
| **5. Citizen App** | Open Citizen Vercel URL | PWA loads, interactive Leaflet map renders with OSM tiles |
| **6. Multilingual** | Toggle Telugu / Hindi / English | Guidance card updates instantly in Telugu |
| **7. SOS Lifecycle** | Submit citizen SOS | Appears in Command Centre feed via WebSocket, poller updates |
| **8. Human Dispatch** | Operator confirms rescue | Status transitions to `DISPATCHED`, zero auto-dispatch |

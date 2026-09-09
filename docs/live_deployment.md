# AI-DisasterGuard — Local Deployment & Operations Guide
**Phase**: 5.5 Production Readiness  
**Target Environment**: Local Full-Stack (Windows / Localhost)  
**Status**: ACTIVE & HEALTHY  

---

## 1. System Architecture Overview

```
                          +--------------------------+
                          |   Human Operator / Web   |
                          +-------------+------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
  +------------------------------+              +------------------------------+
  |   Command Centre Frontend    |              |     Citizen Mobile Web       |
  |     (Port 3000 / Vite)       |              |      (Port 3001 / Vite)      |
  +--------------+---------------+              +--------------+---------------+
                 | Proxy: /api                                 | Proxy: /api
                 | Proxy: ws://                                |
                 +----------------------+----------------------+
                                        |
                         +-----------------------------+
                         |    FastAPI Core Engine      |
                         |    (Port 8000 / Uvicorn)    |
                         +--------------+--------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
  +-----------------------------+               +------------------------------+
  |   PostgreSQL 18 Database    |               |  Real Historical ML Engines  |
  |     (Port 5432 / PostGIS)   |               |   (4 Multi-Horizon Models)   |
  +-----------------------------+               +------------------------------+
```

---

## 2. Verified Local Access Endpoints

| Service | Access URL | Type | Status |
| :--- | :--- | :--- | :--- |
| **Command Centre** | `http://localhost:3000` | Full Command & Control Dashboard | **200 OK — Active** |
| **Citizen App** | `http://localhost:3001` | Citizen Emergency & SOS Interface | **200 OK — Active** |
| **FastAPI Backend** | `http://localhost:8000` | Core Intelligence REST API | **200 OK — Active** |
| **System Health API** | `http://localhost:8000/health` | Comprehensive Health Telemetry | **200 OK — Healthy** |
| **Interactive API Docs**| `http://localhost:8000/docs` | OpenAPI Swagger Documentation | **200 OK — Active** |
| **WebSocket Stream** | `ws://localhost:8000/api/v1/ws` | Real-time Operations Event Bus | **Connected — Online** |

---

## 3. Component Configuration & Environment

### A. FastAPI Backend (`backend/.env`)
- Database URL: `postgresql://postgres:udaychowdary@127.0.0.1:5432/disasterguard`
- Fallback SQLite: Disabled (`ALLOW_SQLITE_FALLBACK=false`)
- Weather Provider: Real live Open-Meteo (`WEATHER_PROVIDER=real`)
- CORS Origins: Explicitly authorized for localhost and 127.0.0.1 on ports 3000, 3001, and 5173
- STT Provider: Whisper / MockSTT fallback enabled for offline reliability

### B. Command Centre Frontend (`vite.config.ts`)
- Port: `3000`
- Reverse Proxy: `/api` -> `http://127.0.0.1:8000` (`changeOrigin: true`, `ws: true`)
- WebSockets: Direct and reverse proxy supported

### C. Citizen Mobile Web (`citizen-app/vite.config.ts`)
- Port: `3001`
- Reverse Proxy: `/api` -> `http://127.0.0.1:8000` (`changeOrigin: true`, `ws: true`)

---

## 4. Startup & Execution Instructions

The services are currently running live as managed background daemons. To restart them manually at any time:

### 1. PostgreSQL 18
Running locally on port 5432 with PostGIS support.

### 2. FastAPI Backend (Port 8000)
```powershell
cd c:\Users\koyau\.gemini\antigravity-ide\scratch\disaster-guard\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

### 3. Command Centre (Port 3000)
```powershell
cd c:\Users\koyau\.gemini\antigravity-ide\scratch\disaster-guard
$env:PATH = "C:\Users\koyau\nodejs;$env:PATH"
npm run dev
```

### 4. Citizen App (Port 3001)
```powershell
cd c:\Users\koyau\.gemini\antigravity-ide\scratch\disaster-guard\citizen-app
$env:PATH = "C:\Users\koyau\nodejs;$env:PATH"
npm run dev
```

---

## 5. Optional: Exposing to Public URL via Cloudflare Tunnel

If you want to test on your phone or provide a live public test link without deploying to third-party hosting:
`cloudflared.exe` is already downloaded and present in the project root.

In an open PowerShell prompt:
```powershell
# Expose Citizen App (Port 3001):
.\cloudflared.exe tunnel --url http://localhost:3001

# Expose Command Centre (Port 3000):
.\cloudflared.exe tunnel --url http://localhost:3000
```
This generates a live, secure HTTPS `*.trycloudflare.com` URL connected directly to your local workstation.

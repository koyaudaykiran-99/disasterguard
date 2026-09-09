# AI DisasterGuard — Production Deployment Guide

## 1. Production Architecture Overview
In a production deployment, AI DisasterGuard operates as a high-availability containerized micro-service stack:
- **Nginx Reverse Proxy**: Terminating SSL/TLS (HTTPS/WSS), serving pre-rendered Vite production build static assets, and routing `/api` and `/ws` to FastAPI.
- **FastAPI / Uvicorn Workers**: High-performance asynchronous API engine with structured logging, connection pooling, and JWT role-based access control.
- **PostgreSQL 18 + PostGIS**: Authoritative relational and spatial database with composite coordinate indexing and ACID guarantees.
- **Scikit-Learn ML Runtime**: In-memory loaded Random Forest (Rainfall v2.0) and Flood Inundation prototype models.

---

## 2. Containerized Deployment with Docker Compose

1. Build and run the entire stack:
```bash
docker-compose up -d --build
```

2. Check service health:
```bash
docker-compose ps
curl http://localhost:8000/health
```

3. View live structured logs:
```bash
docker-compose logs -f backend
```

---

## 3. Production Security Checklist

- [x] **Secret Isolation**: All API keys, passwords, and JWT secret tokens are supplied via environment variables or secret vaults. No secrets in source control.
- [x] **Client-Side Sanitization**: Zero API keys or database connection strings bundled into frontend production artifacts (`dist/`).
- [x] **CORS Origin Restriction**: Wildcard CORS (`*`) is disabled in production mode. Only explicit frontend domains are whitelisted.
- [x] **Human-in-the-Loop Safeguards**: AI Emergency Agent can never autonomously dispatch rescue units; all tactical actions require human operator confirmation.
- [x] **Safe Error Responses**: Stack traces and raw internal exceptions are suppressed in API error payloads and logged strictly to server-side telemetry.

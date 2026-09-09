@echo off
echo ========================================================
echo Starting AI DisasterGuard Full Stack System...
echo ========================================================

REM Add Node to PATH for this session if not present
SET PATH=%PATH%;C:\Users\%USERNAME%\nodejs

echo Starting FastAPI Backend (Port 8000)...
start "AI DisasterGuard - Backend" cmd /k "cd backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Starting Vite Frontend (Port 3000)...
start "AI DisasterGuard - Frontend" cmd /k "npm run dev"

echo.
echo ========================================================
echo System successfully launched!
echo Frontend: http://localhost:3000
echo Backend Docs: http://127.0.0.1:8000/docs
echo ========================================================

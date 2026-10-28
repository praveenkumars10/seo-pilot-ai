@echo off
echo ========================================================
echo Starting SEO Pilot AI - Autonomous SEO Platform
echo ========================================================

echo [1/2] Launching Backend FastAPI Server (port 8000)...
start "SEO Pilot Backend" cmd /k ".\backend\venv\Scripts\python .\backend\run.py"

echo [2/2] Launching Frontend Vite Dashboard (port 5173)...
start "SEO Pilot Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application successfully launched!
echo Access the Dashboard at: http://localhost:5173
echo API Documentation at:    http://localhost:8000/docs
echo ========================================================

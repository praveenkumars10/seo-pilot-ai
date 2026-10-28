# SEO Pilot AI Local Startup Script for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Launching SEO Pilot AI Autonomous Platform..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Start Backend in separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\backend\venv\Scripts\python .\backend\run.py"

# 2. Start Frontend in separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev"

Write-Host "Both processes initiated!" -ForegroundColor Green
Write-Host "Frontend Dashboard: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Backend API Docs:   http://localhost:8000/docs" -ForegroundColor Yellow

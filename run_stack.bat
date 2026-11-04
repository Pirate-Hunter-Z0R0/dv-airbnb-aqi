@echo off
echo ========================================================
echo  Starting Clean Air Airbnb (FastAPI Backend + React UI)
echo ========================================================

start "Clean Air Airbnb - Backend" cmd /k "cd /d e:\Project\dv-project\clean-air-airbnb\backend && python server.py"
start "Clean Air Airbnb - Frontend" cmd /k "cd /d e:\Project\dv-project\clean-air-airbnb\frontend && npm run dev"

echo Backend starting on http://localhost:8000
echo Frontend starting on http://localhost:5173
echo.

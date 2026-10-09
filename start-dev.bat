@echo off
rem Starts the backend (port 8000) and the frontend (port 5173) in two windows.
rem Close both windows (or press Ctrl+C in each) to stop the app.

start "Plant Health - Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe run.py"
start "Plant Health - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend:  http://127.0.0.1:8000   (API docs: http://127.0.0.1:8000/docs)
echo Frontend: http://localhost:5173
echo.
pause

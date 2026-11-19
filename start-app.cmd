@echo off
setlocal
cd /d "%~dp0"

if /i "%~1"=="backend" goto backend
if /i "%~1"=="frontend" goto frontend

if not exist "backend\venv\Scripts\python.exe" (
    echo Backend environment missing. Complete the Backend Setup in README.md first.
    pause
    exit /b 1
)
where node >nul 2>&1
if errorlevel 1 (
    echo Node.js is missing from PATH. Install Node.js and try again.
    pause
    exit /b 1
)
if not exist "frontend\node_modules\next\dist\bin\next" (
    echo Frontend dependencies missing. Run pnpm install in frontend first.
    pause
    exit /b 1
)

start "Capstone Backend" cmd /d /c call "%~f0" backend
start "Capstone Frontend" cmd /d /c call "%~f0" frontend
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5001
echo Wait for both windows to finish starting, then open the frontend URL.
echo Close the two server windows to stop the app.
pause
exit /b 0

:backend
title Capstone Backend
cd /d "%~dp0backend"
set "PYTHONPATH=."
set "PYTHONUTF8=1"
set "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=true"
set "DOCKER_CONTAINER=false"
set "PORT=5001"
if not defined OLLAMA_HOST set "OLLAMA_HOST=http://localhost:11434"
"venv\Scripts\python.exe" api\app.py
echo.
echo Backend stopped.
pause
exit /b

:frontend
title Capstone Frontend
cd /d "%~dp0frontend"
set "NEXT_PUBLIC_API_URL=http://localhost:5001"
node node_modules\next\dist\bin\next dev --turbopack --port 3000
echo.
echo Frontend stopped.
pause
exit /b

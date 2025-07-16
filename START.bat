@echo off
echo 🚀 Starting CV Updater Application...
echo.

if not exist "frontend\package.json" (
    echo ❌ Error: frontend folder not found!
    echo Please run this from the CV-updater project root directory.
    pause
    exit /b 1
)

if not exist "backend\main_enhanced.py" (
    echo ❌ Error: backend folder not found!
    echo Please run this from the CV-updater project root directory.
    pause
    exit /b 1
)

echo 📦 Starting Backend Server...
start "Backend Server" cmd /c "cd backend && python main_enhanced.py"

echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 🌐 Starting Frontend Server...
start "Frontend Server" cmd /c "cd frontend && npm start"

echo.
echo ✅ Both servers are starting!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo.
echo 📋 What you can do:
echo   1. Go to http://localhost:3000
echo   2. Sign up or login
echo   3. Upload your CV
echo   4. Chat with AI to update CV
echo   5. Download enhanced CV
echo.
echo 🔧 To stop: Close the server windows
echo.
echo Press any key to continue...
pause >nul 
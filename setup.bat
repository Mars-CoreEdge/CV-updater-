@echo off
echo ========================================
echo CV Updater - Complete Setup Script
echo ========================================
echo.

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python is installed
)

echo.
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js is installed
)

echo.
echo [3/6] Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
) else (
    echo ✅ Python dependencies installed
)
cd ..

echo.
echo [4/6] Installing Node.js dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
) else (
    echo ✅ Node.js dependencies installed
)
cd ..

echo.
echo [5/6] Setting up environment files...
if not exist "backend\.env" (
    echo Creating backend environment file...
    copy "backend\env.example" "backend\.env"
    echo ⚠️  Please edit backend\.env with your API keys
) else (
    echo ✅ Backend environment file exists
)

if not exist "frontend\.env" (
    echo Creating frontend environment file...
    copy "frontend\env.example" "frontend\.env"
    echo ⚠️  Please edit frontend\.env with your Supabase keys
) else (
    echo ✅ Frontend environment file exists
)

echo.
echo [6/6] Initializing database...
cd backend
python -c "from main_enhanced import init_db; init_db()"
if errorlevel 1 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
) else (
    echo ✅ Database initialized
)
cd ..

echo.
echo ========================================
echo 🎉 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend\.env with your OpenAI API key
echo 2. Edit frontend\.env with your Supabase credentials
echo 3. Run start_all.bat to start the application
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
pause 
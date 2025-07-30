Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CV Updater - Complete Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/6] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 16+ from https://nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[3/6] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
try {
    pip install -r requirements.txt
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "[4/6] Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location frontend
try {
    npm install
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "[5/6] Setting up environment files..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend environment file..." -ForegroundColor Yellow
    Copy-Item "backend\env.example" "backend\.env"
    Write-Host "⚠️  Please edit backend\.env with your API keys" -ForegroundColor Yellow
} else {
    Write-Host "✅ Backend environment file exists" -ForegroundColor Green
}

if (-not (Test-Path "frontend\.env")) {
    Write-Host "Creating frontend environment file..." -ForegroundColor Yellow
    Copy-Item "frontend\env.example" "frontend\.env"
    Write-Host "⚠️  Please edit frontend\.env with your Supabase keys" -ForegroundColor Yellow
} else {
    Write-Host "✅ Frontend environment file exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[6/6] Initializing database..." -ForegroundColor Yellow
Set-Location backend
try {
    python -c "from main_enhanced import init_db; init_db()"
    Write-Host "✅ Database initialized" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to initialize database" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Edit backend\.env with your OpenAI API key" -ForegroundColor Yellow
Write-Host "2. Edit frontend\.env with your Supabase credentials" -ForegroundColor Yellow
Write-Host "3. Run start_all.ps1 to start the application" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue" 
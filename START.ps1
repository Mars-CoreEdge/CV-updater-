Write-Host "🚀 Starting CV Updater Application..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend/package.json") -or -not (Test-Path "backend/main_enhanced.py")) {
    Write-Host "❌ Error: Make sure you're running this from the CV-updater project root directory" -ForegroundColor Red
    Write-Host "This directory should contain 'frontend' and 'backend' folders" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "📦 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; Write-Host 'Backend Server Starting...' -ForegroundColor Green; python main_enhanced.py"

Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

Write-Host "🌐 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; Write-Host 'Frontend Server Starting...' -ForegroundColor Green; npm start"

Write-Host ""
Write-Host "✅ Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 What you can do now:" -ForegroundColor White
Write-Host "  1. Go to http://localhost:3000" -ForegroundColor Gray
Write-Host "  2. Sign up or login with your account" -ForegroundColor Gray
Write-Host "  3. Upload your CV (PDF/TXT/DOCX)" -ForegroundColor Gray
Write-Host "  4. Chat with AI to update your CV" -ForegroundColor Gray
Write-Host "  5. Download your enhanced CV" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 To stop servers: Close the two PowerShell windows that opened" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor White
Read-Host 
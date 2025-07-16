@echo off
echo ========================================
echo 🤖 CV Chat Test - Quick Start
echo ========================================
echo.
echo Starting backend and frontend...
echo.

REM Start backend in new window
start "CV Backend" cmd /k "cd backend && python main_enhanced.py"

REM Wait a moment for backend to start
timeout /t 3

REM Start frontend in new window  
start "CV Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ Backend starting at: http://localhost:8000
echo ✅ Frontend starting at: http://localhost:3000
echo.
echo 📝 Test Steps:
echo 1. Upload a CV file
echo 2. Try: "What experience do I have?"
echo 3. Try: "I learned React and Node.js"  
echo 4. Try: "Generate CV"
echo.
echo 🎯 The chat now has FULL ACCESS to your CV!
echo.
pause 
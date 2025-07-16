@echo off
echo ========================================
echo 🔧 CV Chat Access Verification
echo ========================================
echo.
echo ✅ FIXED COMPONENTS:
echo   - ChatInterface.js    : Uses backend API
echo   - CVDisplay.js        : Uses backend API  
echo   - FileUpload.js       : Uses backend API
echo.
echo 🎯 ALL COMPONENTS NOW USE SAME DATABASE!
echo.
echo 📋 VERIFICATION STEPS:
echo.
echo 1. Start Backend:
echo    cd backend ^&^& python main_enhanced.py
echo.
echo 2. Start Frontend: 
echo    cd frontend ^&^& npm start
echo.
echo 3. Test Upload:
echo    - Upload a CV file
echo    - Check right panel shows content
echo.
echo 4. Test Chat Access:
echo    - "What experience do I have?"
echo    - "What skills do I have?"
echo    - "I learned Python and React"
echo    - "Generate CV"
echo.
echo 🎉 EXPECTED RESULTS:
echo ✅ Chat shows your actual CV content
echo ✅ Chat can add/edit CV information
echo ✅ Right panel updates in real-time
echo ✅ No more "I don't have access" errors
echo.
echo Starting servers now...
echo.

REM Start backend
start "CV Backend API" cmd /k "cd backend && python main_enhanced.py"

REM Wait for backend to start
timeout /t 4

REM Start frontend
start "CV Frontend" cmd /k "cd frontend && npm start"

echo.
echo 🚀 Servers starting...
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo.
echo 📝 Now test the chat access with these commands:
echo   "What experience do I have?"
echo   "What skills do I have?" 
echo   "I learned JavaScript and Node.js"
echo.
pause 
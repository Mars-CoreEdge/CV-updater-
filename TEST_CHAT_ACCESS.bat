@echo off
echo ========================================
echo 🔧 CV CHAT ACCESS TEST
echo ========================================
echo.
echo This test will verify that the chat system
echo can properly access uploaded files and 
echo perform CRUD operations.
echo.
echo 📋 Test Steps:
echo 1. Check backend API connection
echo 2. Upload sample CV file
echo 3. Test CV content retrieval
echo 4. Test chat access to CV content
echo 5. Test CRUD operations
echo.
echo ⚠️  REQUIREMENTS:
echo - Backend must be running on port 8000
echo - Python requests library must be installed
echo.
echo Starting test in 3 seconds...
timeout /t 3 /nobreak >nul
echo.

python TEST_CHAT_ACCESS.py

echo.
echo ========================================
echo 🎯 TEST COMPLETED
echo ========================================
echo.
echo If tests PASSED:
echo ✅ Chat has full access to file content
echo ✅ CRUD operations working correctly
echo ✅ You can now use the frontend safely
echo.
echo If tests FAILED:
echo ❌ Check backend server is running
echo ❌ Check Python requirements installed
echo ❌ Check file upload permissions
echo.
echo Next: Start frontend with 'cd frontend && npm start'
echo.
pause 
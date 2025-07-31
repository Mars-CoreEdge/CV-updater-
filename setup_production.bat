@echo off
echo 🚀 CV Updater Production Setup Script
echo ======================================
echo.

echo 📋 Your Production URLs:
echo Frontend: https://cv-updater-dwj2.vercel.app
echo Backend:  https://cv-updater-backend-version1.onrender.com
echo.

echo 🔍 Testing Backend Connection...
curl -s https://cv-updater-backend-version1.onrender.com/test
echo.
echo.

echo ✅ Configuration Status:
echo.

echo Frontend (.env):
if exist "frontend\.env" (
    echo ✅ frontend\.env exists
    findstr "REACT_APP_API_URL" frontend\.env
) else (
    echo ❌ frontend\.env missing
)
echo.

echo Backend (.env):
if exist "backend\.env" (
    echo ✅ backend\.env exists
    findstr "CORS_ORIGINS" backend\.env
) else (
    echo ❌ backend\.env missing
)
echo.

echo 📝 Next Steps:
echo 1. Update Vercel environment variables
echo 2. Update Render environment variables  
echo 3. Push code changes: git add . && git commit -m "Production setup" && git push
echo 4. Test your application at https://cv-updater-dwj2.vercel.app
echo.

echo 🎯 Quick Test Commands:
echo curl https://cv-updater-backend-version1.onrender.com/test
echo curl https://cv-updater-dwj2.vercel.app
echo.

pause 
@echo off
echo Setting up CV Updater Chatbot...

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing Node.js dependencies...
cd frontend
npm install

echo.
echo Setup complete!
echo Run start_backend.bat and start_frontend.bat to start the application.
pause 
@echo off
echo ========================================
echo    Advanced Audio Silence Trimmer
echo    Launching Application...
echo ========================================
echo.

REM Launch the Streamlit application in background
start /B streamlit run app.py --server.headless true --server.port 8501

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Open the browser automatically
start http://localhost:8501

echo Application is starting...
echo Browser should open automatically.
echo.
echo To stop the application, close this window or press Ctrl+C.
echo.

REM Keep the window open
pause 
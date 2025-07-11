@echo off
echo ========================================
echo    Advanced Audio Silence Trimmer
echo    Launching Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first to set up the environment
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import streamlit, pydub, librosa, numpy, scipy, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Required packages are not installed
    echo Please run install.bat first to install dependencies
    echo.
    pause
    exit /b 1
)

echo Dependencies OK!
echo.

REM Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please ensure you're running this script from the correct folder
    echo.
    pause
    exit /b 1
)

echo Starting Advanced Audio Silence Trimmer...
echo.
echo The application will open in your default web browser.
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo To stop the application, press Ctrl+C in this window.
echo.

REM Launch the Streamlit application
streamlit run app.py --server.headless true --server.port 8501

REM If we get here, the application has been closed
echo.
echo Application closed.
echo.
pause 
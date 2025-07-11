@echo off
echo ========================================
echo    Advanced Audio Silence Trimmer
echo    Installation Script
echo ========================================
echo.

echo Installing Python dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Detected Python version: %PYTHON_VERSION%
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing required packages...
echo.

REM Upgrade pip and setuptools first
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

REM Try installing with safe requirements first
echo Installing audio processing libraries (safe versions)...
pip install -r requirements_safe.txt

if errorlevel 1 (
    echo.
    echo Trying alternative installation method...
    echo.
    
    REM Try installing packages one by one
    echo Installing packages individually...
    pip install setuptools wheel
    pip install pydub
    pip install streamlit==1.28.0
    pip install numpy==1.24.3
    pip install scipy==1.11.4
    pip install librosa==0.10.1
    pip install soundfile==0.12.1
    pip install matplotlib==3.7.2
    
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install some dependencies
        echo This might be due to missing system libraries
        echo.
        echo For Windows users, you may need to install:
        echo - Microsoft Visual C++ Build Tools
        echo - FFmpeg (for audio processing)
        echo.
        echo Download FFmpeg from: https://ffmpeg.org/download.html
        echo Add FFmpeg to your system PATH
        echo.
        echo Alternative solutions:
        echo 1. Try using Python 3.11 instead of 3.12
        echo 2. Install Microsoft Visual C++ Build Tools
        echo 3. Use conda instead of pip
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo All dependencies have been installed successfully.
echo.
echo To run the application:
echo 1. Double-click run.bat
echo 2. Or run: streamlit run app.py
echo.
echo The application will open in your web browser.
echo.
pause 
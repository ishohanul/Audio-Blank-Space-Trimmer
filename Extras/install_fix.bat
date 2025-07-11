@echo off
echo ========================================
echo    Advanced Audio Silence Trimmer
echo    Installation Fix Script
echo ========================================
echo.

echo This script will try multiple installation methods
echo to handle Python 3.12 compatibility issues.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
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

REM Method 1: Try minimal installation first
echo ========================================
echo Method 1: Installing minimal requirements
echo ========================================
echo.

echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo Installing minimal requirements...
pip install -r requirements_minimal.txt

if not errorlevel 1 (
    echo.
    echo SUCCESS: Minimal installation completed!
    echo You can now run the simple version with: streamlit run app_simple.py
    echo.
    goto :success
)

echo.
echo Method 1 failed. Trying Method 2...
echo.

REM Method 2: Try safe requirements
echo ========================================
echo Method 2: Installing safe requirements
echo ========================================
echo.

pip install -r requirements_safe.txt

if not errorlevel 1 (
    echo.
    echo SUCCESS: Safe installation completed!
    echo You can now run the full version with: streamlit run app.py
    echo.
    goto :success
)

echo.
echo Method 2 failed. Trying Method 3...
echo.

REM Method 3: Install packages individually
echo ========================================
echo Method 3: Installing packages individually
echo ========================================
echo.

echo Installing packages one by one...
pip install setuptools wheel
pip install pydub
pip install streamlit==1.28.0

if not errorlevel 1 (
    echo.
    echo SUCCESS: Basic packages installed!
    echo You can now run the simple version with: streamlit run app_simple.py
    echo.
    goto :success
)

echo.
echo Method 3 failed. Trying Method 4...
echo.

REM Method 4: Try with older Python versions
echo ========================================
echo Method 4: Trying with compatible versions
echo ========================================
echo.

echo Installing older, more compatible versions...
pip install setuptools==65.0.0
pip install wheel==0.38.0
pip install pydub==0.25.1
pip install streamlit==1.24.0

if not errorlevel 1 (
    echo.
    echo SUCCESS: Compatible versions installed!
    echo You can now run the simple version with: streamlit run app_simple.py
    echo.
    goto :success
)

echo.
echo All methods failed. Providing troubleshooting info...
echo.

echo ========================================
echo    TROUBLESHOOTING
echo ========================================
echo.
echo The installation failed. Here are some solutions:
echo.
echo 1. INSTALL VISUAL C++ BUILD TOOLS:
echo    - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo    - Install "C++ build tools" workload
echo.
echo 2. USE PYTHON 3.11 INSTEAD:
echo    - Python 3.12 has compatibility issues with some packages
echo    - Download Python 3.11 from: https://python.org/downloads/
echo.
echo 3. USE CONDA INSTEAD OF PIP:
echo    - Install Anaconda or Miniconda
echo    - Run: conda install pydub streamlit
echo.
echo 4. INSTALL FFMPEG:
echo    - Download from: https://ffmpeg.org/download.html
echo    - Add to system PATH
echo.
echo 5. TRY THE SIMPLE VERSION:
echo    - The simple version uses fewer dependencies
echo    - It should work with just pydub and streamlit
echo.
pause
exit /b 1

:success
echo ========================================
echo    INSTALLATION SUCCESSFUL!
echo ========================================
echo.
echo To run the application:
echo.
echo For simple version (recommended):
echo   streamlit run app_simple.py
echo.
echo For full version (if all dependencies installed):
echo   streamlit run app.py
echo.
echo Or use the batch files:
echo   run.bat
echo.
echo The application will open in your web browser.
echo.
pause 
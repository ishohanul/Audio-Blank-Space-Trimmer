# Advanced Audio Silence Trimmer - Launch Script
# PowerShell Version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Advanced Audio Silence Trimmer" -ForegroundColor Yellow
Write-Host "   Launching Application..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please run install.ps1 first to set up the environment" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Green
try {
    python -c "import streamlit, pydub, librosa, numpy, scipy, matplotlib" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies OK!" -ForegroundColor Green
    } else {
        throw "Dependencies missing"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Required packages are not installed" -ForegroundColor Red
    Write-Host "Please run install.ps1 first to install dependencies" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if app.py exists
if (-not (Test-Path "app.py")) {
    Write-Host "❌ ERROR: app.py not found in current directory" -ForegroundColor Red
    Write-Host "Please ensure you're running this script from the correct folder" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Application files found" -ForegroundColor Green
Write-Host ""

Write-Host "Starting Advanced Audio Silence Trimmer..." -ForegroundColor Green
Write-Host ""
Write-Host "The application will open in your default web browser." -ForegroundColor Yellow
Write-Host "If it doesn't open automatically, go to: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the application, press Ctrl+C in this window." -ForegroundColor Yellow
Write-Host ""

# Launch the Streamlit application
try {
    streamlit run app.py --server.headless true --server.port 8501
} catch {
    Write-Host ""
    Write-Host "Application closed or encountered an error." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Application closed." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit" 
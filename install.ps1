# Advanced Audio Silence Trimmer - Installation Script
# PowerShell Version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Advanced Audio Silence Trimmer" -ForegroundColor Yellow
Write-Host "   Installation Script" -ForegroundColor Yellow
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
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if pip is available
Write-Host "Checking pip availability..." -ForegroundColor Green
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pip found: $pipVersion" -ForegroundColor Green
    } else {
        throw "pip not found"
    }
} catch {
    Write-Host "❌ ERROR: pip is not available" -ForegroundColor Red
    Write-Host "Please ensure pip is installed with Python" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Warning: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""

# Install requirements
Write-Host "Installing audio processing libraries..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to install some dependencies" -ForegroundColor Red
    Write-Host "This might be due to missing system libraries" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For Windows users, you may need to install:" -ForegroundColor Yellow
    Write-Host "- Microsoft Visual C++ Build Tools" -ForegroundColor Yellow
    Write-Host "- FFmpeg (for audio processing)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download FFmpeg from: https://ffmpeg.org/download.html" -ForegroundColor Cyan
    Write-Host "Add FFmpeg to your system PATH" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All dependencies have been installed successfully." -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "1. Double-click run.ps1 (PowerShell)" -ForegroundColor White
Write-Host "2. Double-click run.bat (Command Prompt)" -ForegroundColor White
Write-Host "3. Or run: streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "The application will open in your web browser." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit" 
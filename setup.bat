@echo off
REM ============================================================================
REM LPU Academic Advisor - Automated Setup Script
REM This script sets up everything needed for seamless Puter authentication
REM ============================================================================

echo.
echo ============================================================================
echo   🦁 LPU Academic Advisor - Automated Setup
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python is installed

REM Change to project directory
cd /d "%~dp0"
echo ✓ Changed to project directory: %CD%

REM Create virtual environment (optional but recommended)
echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully

REM Check if .env exists
if exist .env (
    echo ✓ .env file exists
    echo.
    echo ⚠️  IMPORTANT: Configure your credentials in .env:
    echo    1. PUTER_MASTER_TOKEN (from https://puter.com/account/api-keys)
    echo    2. OPENAI_API_KEY (from https://platform.openai.com/api-keys)
    echo    3. DATABASE_URL (your Aiven PostgreSQL URL)
    echo.
) else (
    echo ❌ ERROR: .env file not found
    pause
    exit /b 1
)

REM Test the authentication service
echo.
echo Testing server-side authentication service...
python puter_auth_service.py

if errorlevel 1 (
    echo ⚠️  Warning: Authentication test failed
    echo This is OK if you haven't configured credentials yet
    echo Configure .env and try again
    echo.
)

echo.
echo ============================================================================
echo   ✓ Setup Complete!
echo ============================================================================
echo.
echo Next steps:
echo   1. Edit .env and add your Puter/OpenAI credentials
echo   2. Run: streamlit run app.py
echo   3. Open http://localhost:8501 in your browser
echo.
echo For full setup instructions, see: AUTOMATION_SETUP_GUIDE.md
echo.
pause

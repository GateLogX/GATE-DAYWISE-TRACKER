@echo off
REM GATE Voice Assistant - Quick Start Script for Windows

echo 🚀 GATE 2027 Voice Assistant - Quick Start
echo ==========================================
echo.

REM Check Python version
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
cd backend
pip install -q -r requirements.txt
cd ..

REM Check if .env exists
if not exist "backend\.env" (
    echo ⚠️  No .env file found!
    echo 📝 Creating .env from template...
    copy backend\.env.example backend\.env
    echo.
    echo ⚠️  IMPORTANT: Please edit backend\.env with your credentials:
    echo    - Twilio Account SID and Auth Token
    echo    - OpenAI API Key
    echo    - Your WhatsApp number
    echo.
    pause
)

REM Convert CSV to Excel if needed
if not exist "video_durations_detailed.xlsx" (
    if exist "video_durations_detailed.csv" (
        echo 📊 Converting CSV to Excel...
        python convert_csv_to_excel.py
    ) else (
        echo ⚠️  No lecture data file found!
        echo    Please ensure video_durations_detailed.csv exists
    )
)

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Start the server: cd backend ^&^& python app.py
echo 2. In another terminal, run: python test_system.py
echo 3. Set up ngrok for WhatsApp webhooks (see SETUP_GUIDE.md)
echo.
echo 📚 Full guide: SETUP_GUIDE.md
echo.

REM Ask if user wants to start server now
set /p start="Start the Flask server now? (y/n) "
if /i "%start%"=="y" (
    echo 🚀 Starting server...
    cd backend
    python app.py
)

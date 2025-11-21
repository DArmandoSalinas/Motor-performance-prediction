@echo off
REM Motor Monitoring System Launcher (Windows)

echo 🚀 Starting Motor Preventive Monitoring System...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

REM Run the application
echo ▶️  Launching dashboard...
echo.
streamlit run app.py

REM Deactivate on exit
deactivate






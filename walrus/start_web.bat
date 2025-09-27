@echo off
REM Start Walrus Web Repository Viewer

echo 🌐 Walrus Web Repository Viewer
echo ================================
echo.

REM Check if virtual environment exists, create if not
if not exist "web_venv" (
    echo 📦 Creating virtual environment...
    python -m venv web_venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call web_venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r web_requirements.txt

echo.
echo 🚀 Starting web server...
echo 📁 Monitoring .walrus/metadata.json for repositories
echo 🔗 Access at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the web server
python web_server.py

pause
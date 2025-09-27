#!/bin/bash
# Start Walrus Web Repository Viewer

echo "🌐 Walrus Web Repository Viewer"
echo "================================"
echo ""

# Check if virtual environment exists, create if not
if [ ! -d "web_venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv web_venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source web_venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r web_requirements.txt

echo ""
echo "🚀 Starting web server..."
echo "📁 Monitoring .walrus/metadata.json for repositories"
echo "🔗 Access at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web server
python3 web_server.py
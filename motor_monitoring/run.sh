#!/bin/bash
# Motor Monitoring System Launcher (Mac/Linux)

echo "🚀 Starting Motor Preventive Monitoring System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Run the application
echo "▶️  Launching dashboard..."
echo ""
streamlit run app.py

# Deactivate on exit
deactivate






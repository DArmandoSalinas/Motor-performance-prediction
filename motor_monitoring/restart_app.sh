#!/bin/bash
# Restart the Streamlit app with cache clearing

echo "Stopping any running Streamlit processes..."
pkill -f streamlit

echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null

echo "Starting Streamlit app..."
cd "$(dirname "$0")"
streamlit run app.py --server.runOnSave true





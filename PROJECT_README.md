# Motor Preventive Monitoring System

**Version:** 1.0.0  
**Status:** Production Ready  

## 📖 Overview
The **Motor Preventive Monitoring System** is an industrial-grade dashboard designed to monitor the health of Sumitomo 3-phase induction motors in real-time. It uses vibration and temperature data to detect anomalies, leveraging multi-speed statistical baselines to provide accurate, interpretable health scores.

## ✨ Key Features
- **Multi-Speed Support**: Pre-configured baselines for 50%, 60%, 75%, 90%, and 100% operating speeds.
- **Real-Time Monitoring**: Live visualization of vibration magnitude and temperature trends.
- **Intelligent Anomaly Detection**: Rule-based statistical analysis (Z-scores) to identify "Caution" and "Danger" states.
- **Health Scoring**: Simple 0-100 health index for vibration and temperature.
- **Robust Connectivity**: Threaded serial reader with auto-reconnection and error handling.
- **Data Replay Mode**: Built-in simulation mode to test the system without live hardware.
- **Premium UI**: Modern, clean interface inspired by Apple's design guidelines.

## 🛠️ Installation

1. **Prerequisites**
   - Python 3.8 or higher
   - Pip package manager

2. **Setup**
   ```bash
   cd motor_monitoring
   pip install -r requirements.txt
   ```

3. **Running the Application**
   - **Mac/Linux:**
     ```bash
     ./run.sh
     ```
   - **Windows:**
     ```cmd
     run.bat
     ```
   - **Manual Start:**
     ```bash
     streamlit run app.py
     ```

## 📊 Usage Guide

### 1. Select Operation Mode
- **Serial (Live)**: Connect your Arduino to a USB port. Select the correct COM port from the sidebar and click "Connect".
- **Replay (Demo)**: Select a pre-recorded CSV file to simulate motor behavior. Perfect for demonstrations or testing.

### 2. Choose Speed Profile
Select the speed profile (e.g., "100% Speed") that matches the current motor operation. The system will load the corresponding statistical baseline for accurate anomaly detection.

### 3. Monitor Health
- **Green (70-100)**: Normal operation.
- **Orange (30-70)**: Warning - Deviations detected. Monitor closely.
- **Red (0-30)**: Critical - Significant anomalies. Inspection recommended.

## 📁 Project Structure
```
motor_monitoring/
├── app.py                  # Main dashboard application
├── serial_reader.py        # Real-time data acquisition
├── anomaly_engine.py       # Logic for health scoring & stats
├── baseline_loader.py      # Manages historical baseline data
├── ui_components.py        # Custom UI styling and widgets
├── data_replay.py          # Simulation module
├── data/                   # CSV files for speed baselines
└── requirements.txt        # Python dependencies
```

## 🔧 Hardware Configuration
The system expects CSV-formatted data over a serial connection (115200 baud):
`timestamp, ax_g, ay_g, az_g, temp_C`

Ensure your microcontroller is configured to stream data in this exact format.

## 📄 License
This project is proprietary and intended for internal industrial monitoring use.



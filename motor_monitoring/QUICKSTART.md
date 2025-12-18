# 🚀 Quick Start Guide

## Super Fast Launch (Recommended)

### On Mac/Linux:
```bash
cd motor_monitoring
./run.sh
```

### On Windows:
```cmd
cd motor_monitoring
run.bat
```

The launcher scripts will:
1. Create a virtual environment (if needed)
2. Install all dependencies automatically
3. Launch the dashboard in your browser

---

## Manual Installation (Alternative)

If the launcher scripts don't work:

### Step 1: Navigate to Project
```bash
cd /Users/diegosalinas/Documents/Prediction/motor_monitoring
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate.bat  # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

---

## First Time Setup

### 1. Open the Dashboard
After running the launcher, your browser will automatically open to:
```
http://localhost:8501
```

### 2. Select Machine Type
In the sidebar, choose the machine you want to monitor:
- **Sumitomo 3-Phase Motor** - For motor monitoring
- **Haas Mini Mill** - For milling machine monitoring

### 3. Configure Data Source (Choose One)

#### Option A: Demo Mode (No Hardware Required)
1. In the sidebar, select **"Replay (Demo)"**
2. Choose a CSV file:
   - **Sumitomo:** `motor_100pct.csv` (recommended)
   - **Haas:** Any trajectory file (baseline uses all files combined)
3. Set playback speed: `1.0x` for real-time
4. Click **"▶️ Start Replay"**

#### Option B: Live Hardware Mode
1. Connect Arduino to USB port
2. In the sidebar, select **"Serial (Live)"**
3. Choose your COM port or use **"Auto-detect"**
4. Click **"🔗 Connect"**

### 4. Select Baseline Profile

**For Sumitomo Motor:**
In the sidebar under **"🎚️ Speed Profile"**, select the baseline that matches your current motor operating speed:
- 50% - Low speed operation
- 60% - Medium-low speed
- 75% - Medium speed
- 90% - High speed
- **100% - Full speed (default)**

**For Haas Mini Mill:**
The baseline automatically combines all trajectory files. Select **"baseline"** profile.

### 4. Monitor Health Metrics

The dashboard shows:
- **Status Card** - Current health state with diagnostic messages
- **Health Gauges** - Vibration, Temperature, and Overall health scores
- **Real-Time Plots** - Live vibration and temperature trends
- **Detailed Metrics** - Numerical values for all parameters
- **System Diagnostics** - Connection status and performance

---

## Understanding the Dashboard

### Health States

| State | Score | Meaning | Action |
|-------|-------|---------|--------|
| 🟢 **Normal** | 70-100 | Operating within baseline | Continue monitoring |
| 🟠 **Caution** | 30-70 | Elevated deviations | Monitor closely |
| 🔴 **Danger** | 0-30 | Critical deviations | Inspect immediately |

### Health Gauges
- **Vibration Health** - Measures vibration magnitude against baseline
- **Temperature Health** - Tracks temperature and rate of change
- **Overall Health** - Combined metric (minimum of both)

### Real-Time Plots
- **Vibration Magnitude** - Shows colored threshold bands:
  - Green zone = Normal
  - Orange zone = Caution
  - Red zone = Danger
- **Temperature** - Temperature trend over time

### Diagnostic Messages
The system provides human-readable explanations:
- ✅ Normal operation confirmations
- ⚠️ Caution alerts for elevated metrics
- 🚨 Danger warnings for critical conditions
- 💚 Overall health assessments

---

## Troubleshooting

### Dashboard won't open
- Check if port 8501 is already in use
- Try: `streamlit run app.py --server.port 8502`

### No baseline files found
- Verify CSV files exist in `motor_monitoring/data/`
- Check file names: `motor_50pct.csv`, `motor_60pct.csv`, etc.

### Serial port not connecting
- Install CH340 or FTDI drivers for your Arduino
- Check Arduino is sending data at 115200 baud
- Verify data format: `timestamp,ax_g,ay_g,az_g,temp_C`

### Replay not starting
- Verify CSV file has all 5 required columns
- Check CSV for data formatting errors
- Try a different CSV file

### Dashboard is slow/laggy
- Close unnecessary browser tabs
- Reduce playback speed in replay mode
- Check CPU usage
- Restart the application

---

## Testing the System

### Quick Demo (1 minute)
1. Launch with `./run.sh` or `run.bat`
2. Select "Replay (Demo)" mode
3. Choose `motor_100pct.csv`
4. Click "▶️ Start Replay"
5. Watch the dashboard update in real-time!

### Full Test (5 minutes)
1. Run replay mode with all 5 baseline files
2. Switch between speed profiles while replaying
3. Observe how health scores change
4. Read diagnostic messages
5. Monitor system statistics

---

## Next Steps

### 1. Collect Your Own Baselines
Use the Arduino data collection script to capture baseline data at different motor speeds.

### 2. Connect Live Hardware
Once comfortable with demo mode, connect your Arduino for real-time monitoring.

### 3. Customize Sensitivity
Edit `anomaly_engine.py` to adjust alert thresholds for your specific motor.

### 4. Deploy for Production
Run the system on a dedicated computer for 24/7 monitoring.

---

## Command Reference

### Start the dashboard:
```bash
streamlit run app.py
```

### Start with specific port:
```bash
streamlit run app.py --server.port 8502
```

### Start without auto-open browser:
```bash
streamlit run app.py --server.headless true
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

---

## Support Resources

- **README.md** - Full documentation
- **Code Comments** - Every function is documented
- **System Diagnostics** - Built-in monitoring panel

---

## Hardware Setup

### Arduino Requirements
- Any Arduino with Serial USB (Uno, Nano, Mega, etc.)
- Accelerometer (ADXL345, MPU6050, or similar)
- Temperature sensor (MLX90614, DHT22, or similar)

### Arduino Code Format
```cpp
// Output format: timestamp,ax_g,ay_g,az_g,temp_C
Serial.print(millis() / 1000.0, 3);
Serial.print(",");
Serial.print(ax, 4);
Serial.print(",");
Serial.print(ay, 4);
Serial.print(",");
Serial.print(az, 4);
Serial.print(",");
Serial.println(temp, 2);
```

### Wiring
- Follow your sensor's datasheet
- Ensure common ground between all sensors
- Use appropriate pull-up resistors for I2C sensors

---

## Tips for Best Results

1. **Collect Good Baselines** - Run motor for 3-5 minutes at each speed
2. **Stable Conditions** - Collect baselines under normal operating conditions
3. **Match Speeds** - Select the baseline that best matches current operation
4. **Monitor Trends** - Watch for gradual changes over time
5. **Document Events** - Note any maintenance or changes

---

**Ready to monitor your motor? Run `./run.sh` (Mac/Linux) or `run.bat` (Windows) to get started!**









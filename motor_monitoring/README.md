# Motor Preventive Monitoring System

🍏 **Premium Apple-Style Real-Time Dashboard for Industrial Motor Health Monitoring**

An industrial-grade, interpretable preventive maintenance system supporting multiple machine types. Features real-time vibration and temperature monitoring with machine-specific baseline profiling and adaptive thresholds.

## Supported Machines

- **Sumitomo 3-Phase Induction Motor** - Multi-speed baseline profiling (50%, 60%, 75%, 90%, 100%)
- **Haas Mini Mill** - Trajectory-based baseline from multiple operational scenarios

---

## 🎯 Features

- **Multi-Machine Support** - Monitor both Sumitomo motors and Haas Mini Mill machines
- **Machine-Specific Baselines** - Automatic baseline creation from operational data
- **Adaptive Thresholds** - Machine-specific sensitivity settings (milling machines use more lenient thresholds)
- **Multi-Speed Baseline Profiling** - Sumitomo supports 50%, 60%, 75%, 90%, and 100% motor speeds
- **Trajectory-Based Baselines** - Haas combines all trajectory files for comprehensive baseline
- **Real-Time Serial Ingestion** - Robust threaded serial reader with auto-reconnection
- **Rule-Based Anomaly Detection** - No ML, fully interpretable statistical analysis
- **Health Scoring System** - Intuitive 0-100 health scores with color-coded states
- **Premium Apple-Style UI** - Beautiful, minimalistic dashboard design
- **Data Replay Mode** - Test and demo without hardware
- **Live Diagnostics** - Packet rates, FPS, buffer status

---

## 🚀 Quick Start

### 1. Installation

```bash
cd motor_monitoring
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### 3. Select Machine Type

In the sidebar, choose the machine you want to monitor:
- **Sumitomo 3-Phase Motor** - For motor monitoring with speed-based baselines
- **Haas Mini Mill** - For milling machine monitoring with trajectory-based baseline

### 4. Configure Data Source

**Option A: Replay Mode (Demo)**
1. Select "Replay (Demo)" in the sidebar
2. Choose a CSV file (one file for replay, baseline uses all files for Haas)
3. Adjust playback speed (1.0x = real-time)
4. Click "▶️ Start Replay"

**Option B: Serial Mode (Live Hardware)**
1. Connect your Arduino to a USB port
2. Select "Serial (Live)" in the sidebar
3. Choose your COM port (or use Auto-detect)
4. Click "🔗 Connect"

### 5. Select Baseline Profile

**For Sumitomo Motor:**
Choose the motor speed profile (50%, 60%, 75%, 90%, 100%) that matches your current operating conditions.

**For Haas Mini Mill:**
The baseline automatically combines all trajectory CSV files. Select "baseline" profile.

---

## 📁 Project Structure

```
motor_monitoring/
│
├── app.py                      # Main Streamlit application
├── serial_reader.py            # Threaded serial port reader
├── baseline_loader.py          # Multi-machine baseline engine
├── anomaly_engine.py           # Rule-based health scoring (machine-specific)
├── ui_components.py            # Apple-style UI components
├── utils.py                    # Helper functions
├── data_replay.py              # CSV simulation mode
│
├── data/                       # Machine-specific baseline data
│   ├── sumitomo/               # Sumitomo motor baselines
│   │   ├── motor_50pct.csv
│   │   ├── motor_60pct.csv
│   │   ├── motor_75pct.csv
│   │   ├── motor_90pct.csv
│   │   └── motor_100pct.csv
│   └── haas/                   # Haas Mini Mill trajectory files
│       ├── motor_data_*.csv    # Multiple trajectory files
│       └── (baseline auto-created from all files)
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 📊 Data Format

All CSV files must contain exactly these columns:

| Column | Description | Unit |
|--------|-------------|------|
| `timestamp` | Unix timestamp | seconds |
| `ax_g` | X-axis acceleration | g |
| `ay_g` | Y-axis acceleration | g |
| `az_g` | Z-axis acceleration | g |
| `temp_C` | Temperature | °C |

**Example:**
```csv
timestamp,ax_g,ay_g,az_g,temp_C
1699564800.123,-0.0245,0.0156,1.0023,45.2
1699564800.223,-0.0251,0.0161,1.0019,45.2
```

---

## 🔧 Serial Configuration

### Arduino Output Format

Your Arduino must output data in this exact CSV format over serial:

```cpp
Serial.print(timestamp);
Serial.print(",");
Serial.print(ax_g, 4);
Serial.print(",");
Serial.print(ay_g, 4);
Serial.print(",");
Serial.print(az_g, 4);
Serial.print(",");
Serial.println(temp_C, 2);
```

### Serial Parameters

- **Baud Rate:** 115200
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None

---

## 🎨 Dashboard Features

### Health Gauges
- **Vibration Health** - Real-time vibration magnitude scoring (baseline comparison)
- **Temperature Health** - Rate of change detection (no baseline, environment-adaptive)
- **Overall Health** - Combined system health metric

### Status States
- 🟢 **Normal** (70-100) - Operating within baseline parameters
- 🟠 **Caution** (30-70) - Elevated deviations, monitor closely
- 🔴 **Danger** (0-30) - Critical deviations, inspection recommended

### Real-Time Plots
- **Vibration Magnitude** - Live 3-axis vibration magnitude with threshold bands
- **Temperature** - Temperature trend with rate of change indicators

### Diagnostic Messages
- Vibration status (baseline deviation)
- Temperature status (rate of change detection)
- Rapid temperature change alerts
- Overall health assessment

---

## 🧮 Health Scoring Algorithm

### Machine-Specific Thresholds

The system uses different sensitivity thresholds based on machine type:

**Sumitomo Motor (Sensitive):**
- Vibration Caution: 1.2σ
- Vibration Danger: 2.0σ
- Temperature Caution: 0.1°C/s
- Temperature Danger: 0.5°C/s
- Max Temperature: 40°C

**Haas Mini Mill (Lenient):**
- Vibration Caution: 3.0σ (milling operations have higher natural vibration)
- Vibration Danger: 4.5σ (allows for cutting variations)
- Temperature Caution: 0.2°C/s
- Temperature Danger: 1.0°C/s
- Max Temperature: 50°C

### Vibration Analysis
1. Compute vibration magnitude: `vib = sqrt(ax² + ay² + az²)`
2. Calculate z-score: `z = (current_mean - baseline_mean) / baseline_std`
3. Apply machine-specific threshold bands (see above)
4. Convert to 0-100 health score

### Temperature Analysis
1. Compute temperature rate of change via linear regression (°C/s)
2. Detect rapid changes (no baseline comparison - temperature varies with environment):
   - Uses machine-specific thresholds (see above)
3. Enforce absolute safety limits (machine-specific max/min temperatures)

### Overall Health
- `overall_health = min(vibration_health, temperature_health)`
- Conservative approach: worst metric determines overall state

---

## 🛠️ Advanced Usage

### Custom Baseline Collection

**For Sumitomo Motor:**
1. Run motor at desired speed for 2-5 minutes
2. Collect data using Arduino and `data_collection_with_timestamps.py`
3. Save as `motor_XXpct.csv` in `data/sumitomo/` folder
4. Restart application to load new baseline

**For Haas Mini Mill:**
1. Collect data from multiple trajectories/scenarios when machine is operating normally
2. Save all trajectory files as `motor_data_*.csv` in `data/haas/` folder
3. The system automatically combines ALL files to create a comprehensive baseline
4. For replay, select individual trajectory files
5. Restart application to load new baseline

### Adjusting Sensitivity

Edit thresholds in `anomaly_engine.py` (machine-specific sections):

**For Sumitomo Motor:**
```python
self.vib_z_caution = 1.2  # Z-score threshold for caution
self.vib_z_danger = 2.0   # Z-score threshold for danger
self.temp_slope_caution = 0.1   # °C/s - Caution threshold
self.temp_slope_danger = 0.5    # °C/s - Danger threshold
self.temp_max_critical = 40.0  # Critical high temperature (°C)
```

**For Haas Mini Mill:**
```python
self.vib_z_caution = 3.0   # More lenient for milling operations
self.vib_z_danger = 4.5    # More lenient for cutting variations
self.temp_slope_caution = 0.2   # °C/s - More lenient
self.temp_slope_danger = 1.0    # °C/s - More lenient
self.temp_max_critical = 50.0  # Higher for milling operations
```

### Customizing UI Colors

Edit color scheme in `ui_components.py`:

```python
APPLE_COLORS = {
    'green': '#34C759',
    'orange': '#FF9500',
    'red': '#FF3B30',
    # ... customize as needed
}
```

---

## 🐛 Troubleshooting

### No Serial Ports Detected
- Ensure Arduino is connected
- Install CH340/FTDI drivers if needed
- Check Device Manager (Windows) or `ls /dev/tty*` (Mac/Linux)

### Connection Drops
- Check USB cable quality
- Verify baud rate matches Arduino (115200)
- Try different USB port
- Add USB hub with external power

### Data Format Errors
- Verify CSV has all 5 required columns
- Check for missing/corrupted values
- Ensure timestamp is Unix format
- Validate acceleration units are in g

### Low FPS / Performance Issues
- Reduce buffer duration in serial_reader.py
- Decrease plot update frequency in app.py
- Close other browser tabs
- Check CPU usage

---

## 📝 License

This is a professional industrial monitoring system. Use in accordance with your organization's policies.

---

## 👨‍💻 System Requirements

- **Python:** 3.8 or higher
- **RAM:** 2GB minimum, 4GB recommended
- **OS:** Windows, macOS, or Linux
- **Browser:** Chrome, Firefox, Safari, or Edge (latest versions)

---

## 🎓 Technical Details

### Sampling Rate
- Target: 10 Hz (adjustable)
- Buffer: 10 seconds rolling window
- Analysis window: 1-2 seconds

### Performance
- UI updates: 5-10 FPS
- Serial ingestion: 10-20 Hz
- Zero UI freezing via threading

### Algorithms
- **Vibration:** Statistical z-score analysis (baseline comparison)
- **Temperature:** Rate of change detection via linear regression (no baseline, environment-adaptive)
- **Safety:** Absolute temperature limits (10-40°C hard cutoffs)
- Conservative health scoring (minimum of vibration and temperature)

---

## 🌐 Deployment

### Deploy to Streamlit Cloud (Recommended)

**Free hosting for Streamlit apps!**

1. Push your code to GitHub
2. Visit https://share.streamlit.io/
3. Connect your repository
4. Set main file: `motor_monitoring/app.py`
5. Deploy!

**⚠️ Important:** Serial port reading won't work on cloud platforms (no hardware access). Users can still use **Replay (Demo)** mode with CSV files.

📖 **Full deployment guide:** See `DEPLOYMENT.md`  
⚡ **Quick start:** See `DEPLOYMENT_QUICKSTART.md`

---

## 📞 Support

For technical questions or issues, review the code comments in each module. All functions are documented with clear docstrings.

**Key modules to review:**
- `baseline_loader.py` - Understanding baseline statistics
- `anomaly_engine.py` - Health scoring logic
- `serial_reader.py` - Serial communication details
- `ui_components.py` - UI customization

---

**Built with ❤️ for industrial preventive maintenance**









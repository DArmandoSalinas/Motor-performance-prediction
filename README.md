# Motor Preventive Monitoring System

**Real-Time Dashboard for Industrial Motor Health Monitoring**

An industrial-grade, interpretable preventive maintenance system for Sumitomo 3-phase induction motors. Features real-time vibration and temperature monitoring with multi-speed baseline profiling.

---

## 🎯 Features

- **Multi-Speed Baseline Profiling** - Supports 50%, 60%, 75%, 90%, and 100% motor speeds
- **Real-Time Serial Ingestion** - Robust threaded serial reader with auto-reconnection
- **Rule-Based Anomaly Detection** - No ML, fully interpretable statistical analysis
- **Health Scoring System** - Intuitive 0-100 health scores with color-coded states
- **Premium Apple-Style UI** - Beautiful, minimalistic dashboard design
- **Data Replay Mode** - Test and demo without hardware
- **Live Diagnostics** - Packet rates, FPS, buffer status

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone and Install

Open your terminal or command prompt and run:

```bash
# Clone the repository
git clone https://github.com/DArmandoSalinas/Motor-performance-prediction.git

# Navigate to the project folder
cd Motor-performance-prediction

# Navigate to the application directory
cd motor_monitoring

# (Optional but recommended) Create and activate a virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### 3. Configure Data Source

**Option A: Replay Mode (Demo)**
1. Select "Replay (Demo)" in the sidebar
2. Choose a baseline CSV file
3. Adjust playback speed (1.0x = real-time)
4. Click "▶️ Start Replay"

**Option B: Serial Mode (Live Hardware)**
1. Connect your Arduino to a USB port
2. Select "Serial (Live)" in the sidebar
3. Choose your COM port (or use Auto-detect)
4. Click "🔗 Connect"

### 4. Select Speed Profile

Choose the motor speed profile (50%, 60%, 75%, 90%, 100%) that matches your current operating conditions.

---

## 📁 Project Structure

```
motor_monitoring/
│
├── app.py                      # Main Streamlit application
├── serial_reader.py            # Threaded serial port reader
├── baseline_loader.py          # Multi-speed baseline engine
├── anomaly_engine.py           # Rule-based health scoring
├── ui_components.py            # Apple-style UI components
├── utils.py                    # Helper functions
├── data_replay.py              # CSV simulation mode
│
├── data/                       # Baseline CSV files
│   ├── motor_50pct.csv
│   ├── motor_60pct.csv
│   ├── motor_75pct.csv
│   ├── motor_90pct.csv
│   └── motor_100pct.csv
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
- **Vibration Health** - Real-time vibration magnitude scoring
- **Temperature Health** - Temperature rate-of-change and limits scoring
- **Overall Health** - Combined system health metric

### Status States
- 🟢 **Normal** (70-100) - Operating within baseline parameters
- 🟠 **Caution** (30-70) - Elevated deviations, monitor closely
- 🔴 **Danger** (0-30) - Critical deviations, inspection recommended

### Real-Time Plots
- **Vibration Magnitude** - Live 3-axis vibration magnitude with threshold bands
- **Temperature** - Temperature trend with baseline comparison

### Diagnostic Messages
- Vibration status
- Temperature status
- Rate-of-change alerts
- Overall health assessment

---

## 🧮 Health Scoring Algorithm

### Vibration Analysis
1. Compute vibration magnitude: `vib = sqrt(ax² + ay² + az²)`
2. Calculate z-score: `z = (current_mean - baseline_mean) / baseline_std`
3. Apply threshold bands:
   - Normal: z ≤ 1.2σ
   - Caution: 1.2σ < z ≤ 2σ
   - Danger: z > 2σ
4. Convert to 0-100 health score

### Temperature Analysis
1. Compute temperature rate of change (°C/s)

### Overall Health
- `overall_health = min(vibration_health, temperature_health)`
- Conservative approach: worst metric determines overall state

---

## 🛠️ Advanced Usage

### Custom Baseline Collection

To create your own baseline profile:

1. Run motor at desired speed for 2-5 minutes
2. Collect data using Arduino and `data_collection_with_timestamps.py`
3. Save as `motor_XXpct.csv` in `data/` folder
4. Restart application to load new baseline

### Adjusting Sensitivity

Edit thresholds in `anomaly_engine.py`:

```python
self.z_caution = 1.2  # Change more sensitive
self.z_danger = 2.0   # Change more sensitive
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
- Moving statistics (mean, std, max)
- Linear regression for temperature slope
- Z-score normalization
- Conservative health scoring

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


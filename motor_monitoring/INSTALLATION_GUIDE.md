# 🎯 Installation & First Run Guide

## ⚡ Super Quick Start (60 seconds)

### Step 1: Navigate to the Project
```bash
cd /Users/diegosalinas/Documents/Prediction/motor_monitoring
```

### Step 2: Launch the Dashboard

**On Mac (You're here!):**
```bash
./run.sh
```

**On Windows:**
```cmd
run.bat
```

### Step 3: Wait for Browser to Open
The dashboard will automatically open at `http://localhost:8501`

### Step 4: Start Demo
1. In the sidebar, select **"Replay (Demo)"** (should be selected by default)
2. CSV file should be **"motor_100pct.csv"**
3. Click the **"▶️ Start Replay"** button
4. Watch your dashboard come alive! 🎉

---

## 🎨 What You'll See

### Main Dashboard Features:

1. **Status Card** (Top)
   - Large colored state indicator (🟢 Green / 🟠 Orange / 🔴 Red)
   - Pulsing status dot
   - List of diagnostic messages
   - Real-time health assessment

2. **Three Health Gauges** (Middle)
   - **Vibration Health** - Left gauge
   - **Temperature Health** - Middle gauge
   - **Overall Health** - Right gauge
   - Each shows 0-100 score with color coding

3. **Live Plots** (Lower Middle)
   - **Vibration Magnitude** - Shows threshold bands (green/orange/red zones)
   - **Temperature Trend** - Real-time temperature plot
   - Both update 5-10 times per second

4. **Detailed Metrics** (Lower)
   - Vibration Mean, Max
   - Temperature, Rate of change
   - Four metric cards in a row

5. **System Diagnostics** (Bottom)
   - Connection status
   - Packet rate
   - Buffer information
   - Error counts

6. **Sidebar Controls** (Left)
   - Mode selection (Replay/Serial)
   - File/port selection
   - Speed profile selector
   - System information
   - Restart button

---

## 🎮 Interactive Controls

### Switching Speed Profiles
1. Look at sidebar: **"🎚️ Speed Profile"**
2. Dropdown shows: 50%, 60%, 75%, 90%, 100%
3. Select different speed
4. Watch thresholds adjust automatically

### Changing Playback Speed
1. In sidebar under **"📼 Replay Settings"**
2. Slider: 0.5x to 5.0x
3. Adjust to speed up or slow down demo
4. Click **"▶️ Start Replay"** to apply

### Restarting Replay
1. Click **"🔄 Restart"** button in sidebar
2. Replay starts from beginning
3. All buffers cleared
4. Fresh analysis begins

---

## 🔧 Troubleshooting

### Dashboard Won't Open
```bash
# Manually install dependencies and run
pip3 install -r requirements.txt
streamlit run app.py
```

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Missing Python Packages
```bash
# Install individually
pip3 install streamlit numpy pandas plotly pyserial
```

### Script Permission Denied (Mac/Linux)
```bash
# Make script executable
chmod +x run.sh
./run.sh
```

---

## 📱 Connecting Your Arduino

### When You're Ready for Live Data:

1. **Connect Arduino** to USB port

2. **In Dashboard Sidebar:**
   - Select **"Serial (Live)"** mode
   - Choose COM port (or use "Auto-detect")
   - Click **"🔗 Connect"**

3. **Verify Arduino Code:**
   Your Arduino must output:
   ```
   timestamp,ax_g,ay_g,az_g,temp_C
   ```
   
   Example Arduino code:
   ```cpp
   Serial.print(millis()/1000.0, 3);
   Serial.print(",");
   Serial.print(ax, 4);
   Serial.print(",");
   Serial.print(ay, 4);
   Serial.print(",");
   Serial.print(az, 4);
   Serial.print(",");
   Serial.println(temp, 2);
   ```

4. **Set Serial to 115200 baud:**
   ```cpp
   Serial.begin(115200);
   ```

---

## 🎓 Understanding Health States

### 🟢 Normal (70-100)
- Vibration within 2σ of baseline
- Temperature stable
- No action needed
- **Message Examples:**
  - "✅ Vibration within normal range"
  - "✅ Temperature stable"
  - "💚 Motor operating normally"

### 🟠 Caution (30-70)
- Vibration between 2σ and 3σ
- Temperature elevated or changing fast
- Monitor closely
- **Message Examples:**
  - "⚠️ Vibration elevated above normal"
  - "⚠️ Temperature rising rapidly (25.0°C, +0.300°C/s)"
  - "⚠️ Minor deviations detected"

### 🔴 Danger (0-30)
- Vibration exceeds 3σ
- Temperature critically high or changing rapidly
- Inspect immediately
- **Message Examples:**
  - "🚨 High vibration detected!"
  - "🚨 Temperature significantly elevated!"
  - "🚨 Critical - immediate inspection recommended!"

---

## 📊 Reading the Plots

### Vibration Magnitude Plot
- **X-axis:** Time (seconds ago)
- **Y-axis:** Vibration magnitude (g)
- **Green band:** Normal zone (0 to mean+2σ)
- **Orange band:** Caution zone (mean+2σ to mean+3σ)
- **Red band:** Danger zone (above mean+3σ)
- **Blue line:** Current vibration
- **Blue shading:** Area under curve

### Temperature Plot
- **X-axis:** Time (seconds ago)
- **Y-axis:** Temperature (°C)
- **Orange line:** Current temperature
- **Orange shading:** Area under curve

---

## 🎯 Quick Test Checklist

Run through this checklist on first launch:

- [ ] Dashboard opens in browser
- [ ] Replay mode is selected
- [ ] Click "▶️ Start Replay"
- [ ] Status card shows messages
- [ ] Health gauges animate
- [ ] Plots update in real-time
- [ ] Can switch speed profiles
- [ ] System diagnostics show data
- [ ] No error messages appear
- [ ] UI looks clean and professional

If all items checked ✅ - **System is working perfectly!**

---

## 💾 Files You Created

```
motor_monitoring/
├── 🐍 Core Python Modules (7 files)
│   ├── app.py                 - Main application
│   ├── baseline_loader.py     - Load baselines
│   ├── serial_reader.py       - Serial communication
│   ├── data_replay.py         - Replay mode
│   ├── anomaly_engine.py      - Health scoring
│   ├── ui_components.py       - UI components
│   └── utils.py               - Helper functions
│
├── 📊 Baseline Data (5 files)
│   └── data/
│       ├── motor_50pct.csv
│       ├── motor_60pct.csv
│       ├── motor_75pct.csv
│       ├── motor_90pct.csv
│       └── motor_100pct.csv
│
├── 📚 Documentation (5 files)
│   ├── README.md              - Main documentation
│   ├── QUICKSTART.md          - Quick start guide
│   ├── ARCHITECTURE.md        - Technical details
│   ├── PROJECT_SUMMARY.md     - Project overview
│   └── INSTALLATION_GUIDE.md  - This file
│
├── 🚀 Launchers (2 files)
│   ├── run.sh                 - Mac/Linux
│   └── run.bat                - Windows
│
└── 📋 Config (1 file)
    └── requirements.txt       - Dependencies

Total: 20 files, ~4,000 lines
```

---

## 🎁 What You Got

### ✅ Complete System
- Multi-speed baseline engine
- Real-time serial ingestion
- Data replay simulation
- Anomaly detection
- Health scoring
- Apple-style dashboard

### ✅ Production Quality
- Robust error handling
- Thread-safe operations
- Auto-reconnection
- Performance monitoring
- Clean, modular code

### ✅ Beautiful UI
- Apple design language
- Smooth animations
- Color-coded states
- Clear visualizations
- Professional appearance

### ✅ Comprehensive Docs
- 2,000+ lines of documentation
- Multiple skill levels covered
- Code examples throughout
- Troubleshooting guides
- Architecture diagrams

---

## 🚀 You're All Set!

Your motor monitoring system is ready to use. Just run:

```bash
./run.sh
```

And start monitoring your motor health in style! 🎉

---

**Need Help?**
- Quick questions → Check **QUICKSTART.md**
- Full features → Read **README.md**
- Technical details → See **ARCHITECTURE.md**
- Overview → Review **PROJECT_SUMMARY.md**

**Have fun monitoring!** 😊









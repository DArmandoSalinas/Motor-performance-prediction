# 🏗️ Technical Architecture

## System Overview

The Motor Preventive Monitoring System is a modular, industrial-grade application built with clean architecture principles. No machine learning is used - all anomaly detection is rule-based and fully interpretable.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        app.py                                │
│                  (Streamlit Application)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ UI Components│  │Session State │  │  Auto-Refresh│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────┬──────────────┬──────────────┬───────────────┘
              │              │              │
              ▼              ▼              ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │Data Source   │  │Baseline      │  │Anomaly       │
    │              │  │Loader        │  │Engine        │
    │- Serial      │  │              │  │              │
    │- Replay      │  │              │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │Threading     │  │Statistical   │  │Health        │
    │Buffers       │  │Signatures    │  │Scoring       │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## Module Breakdown

### 1. `app.py` - Main Application
**Role:** Orchestration and UI rendering

**Key Functions:**
- `init_session_state()` - Initialize Streamlit session
- `load_baselines()` - Load baseline CSV files
- `initialize_data_source()` - Set up Serial or Replay mode
- `update_anomaly_engine()` - Switch baseline profiles
- `render_sidebar()` - Control panel
- `render_main_dashboard()` - Main display

**Data Flow:**
1. Load baselines on startup
2. Initialize data source (Serial/Replay)
3. Create anomaly engine with selected baseline
4. Loop: Get data → Analyze → Render → Refresh

**Key Design Patterns:**
- Singleton pattern for session state
- Observer pattern for data source
- Auto-refresh loop with Streamlit rerun

---

### 2. `baseline_loader.py` - Multi-Speed Profile Engine
**Role:** Load and process baseline CSV files

**Key Class:** `BaselineLoader`

**Key Methods:**
- `load_all_baselines()` - Batch load all speed profiles
- `_load_baseline(csv_path, speed)` - Process single baseline
- `get_baseline(speed)` - Retrieve specific baseline
- `print_summary()` - Display baseline statistics

**Statistical Computations:**
```python
For each baseline:
  - vib_mag = sqrt(ax² + ay² + az²)
  - vib_mean, vib_std
  - threshold_normal = mean + 2σ
  - threshold_caution = mean + 3σ
  - temp_mean, temp_std
  - temp_rate (°C/s via linear regression)
```

**Output Structure:**
```python
{
  "speed": "100",
  "vib_mean": float,
  "vib_std": float,
  "threshold_normal": float,
  "threshold_caution": float,
  "temp_mean": float,
  "temp_std": float,
  "temp_rate_mean": float,
  "temp_rate_std": float,
  # ... more statistics
}
```

---

### 3. `serial_reader.py` - Serial Port Communication
**Role:** Threaded real-time data acquisition

**Key Class:** `SerialReader`

**Architecture:**
- **Main Thread:** Streamlit UI
- **Reader Thread:** Non-blocking serial reading
- **Thread-Safe:** Lock-protected buffer operations

**Key Methods:**
- `auto_detect_port()` - Find Arduino automatically
- `connect()` - Establish serial connection
- `start()` - Launch reader thread
- `_read_loop()` - Continuous reading (threaded)
- `get_recent_data(duration)` - Extract windowed data

**Buffer Management:**
- Rolling deque with 10-second window
- Automatic old data trimming
- Thread-safe access with locks

**Error Handling:**
- Auto-reconnection on disconnect
- Packet validation
- Graceful error recovery

**Performance:**
- Non-blocking I/O
- FPS tracking
- Drop rate monitoring

---

### 4. `data_replay.py` - CSV Simulation Mode
**Role:** Replay CSV data as real-time stream

**Key Class:** `DataReplay`

**Interface:** Identical to `SerialReader` for seamless swapping

**Key Features:**
- Adjustable playback speed (0.5x - 5x)
- Looping support
- Timestamp synchronization
- Progress tracking

**Timing Algorithm:**
```python
elapsed_data = (current_timestamp - start_timestamp) / playback_speed
target_time = real_start_time + elapsed_data
sleep(target_time - current_time)
```

**Use Cases:**
- Demo without hardware
- Development and testing
- Presentations
- Algorithm tuning

---

### 5. `anomaly_engine.py` - Health Scoring Logic
**Role:** Rule-based anomaly detection and health scoring

**Key Class:** `AnomalyEngine`

**Core Algorithm:**

#### Vibration Analysis:
```python
1. Compute vib_mag = sqrt(ax² + ay² + az²)
2. Calculate statistics: mean, std, max
3. Compute z-score: z = (current - baseline_mean) / baseline_std
4. Map z-score to health score:
   - |z| ≤ 2σ → 100-70 (Normal)
   - 2σ < |z| ≤ 3σ → 70-30 (Caution)
   - |z| > 3σ → 30-0 (Danger)
```

#### Temperature Analysis:
```python
1. Compute temp_slope via linear regression (rate of change)
2. Detect rapid changes (no baseline comparison):
   - Normal: |slope| < 0.1 °C/s
   - Caution: 0.1 ≤ |slope| < 0.5 °C/s
   - Danger: |slope| ≥ 0.5 °C/s
3. Enforce absolute limits: temp ≥ 40°C or ≤ 10°C → Health = 0%
```

#### Overall Health:
```python
overall_health = min(vib_health, temp_health)
```

**Key Methods:**
- `analyze(data, window)` - Main analysis function
- `_analyze_vibration(vib_mag)` - Vibration metrics
- `_analyze_temperature(temps, times)` - Temperature metrics
- `_generate_messages(vib, temp)` - Human-readable diagnostics

**Output Structure:**
```python
{
  "vib_health_score": 0-100,
  "vib_state": "Normal|Caution|Danger",
  "vib_color": "#hex",
  "temp_health_score": 0-100,
  "temp_state": "Normal|Caution|Danger",
  "temp_color": "#hex",
  "overall_health_score": 0-100,
  "overall_state": "Normal|Caution|Danger",
  "messages": ["...", "..."],
  # ... detailed metrics
}
```

---

### 6. `ui_components.py` - Apple-Style UI
**Role:** Premium dashboard components

**Design System:**
- **Typography:** Inter font (SF Pro alternative)
- **Colors:** Apple Human Interface Guidelines
- **Spacing:** 8px grid system
- **Shadows:** Subtle elevation
- **Animations:** Smooth transitions

**Key Components:**

#### `apply_apple_style()`
- Injects custom CSS
- Removes Streamlit branding
- Applies design system

#### `render_health_gauge(label, value, color)`
- Plotly circular gauge
- Smooth animations
- Color-coded indicators

#### `render_status_card(state, color, messages)`
- Card-based layout
- Pulsing status indicator
- Message list

#### `render_time_series_plot(...)`
- Line charts with threshold bands
- Color-coded zones
- Unified hover mode

#### `render_metric_row(metrics)`
- Grid layout
- Label + Value + Unit
- Consistent styling

**Color Palette:**
```python
APPLE_COLORS = {
  'green': '#34C759',   # Success
  'orange': '#FF9500',  # Warning
  'red': '#FF3B30',     # Danger
  'blue': '#007AFF',    # Info
  'gray': '#8E8E93',    # Neutral
}
```

---

### 7. `utils.py` - Helper Functions
**Role:** Shared utility functions

**Categories:**

#### Signal Processing:
- `compute_vibration_magnitude()` - 3D magnitude
- `compute_temperature_slope()` - Linear regression
- `smooth_data()` - Moving average

#### Statistics:
- `compute_z_score()` - Normalization
- `health_score_from_z()` - Score mapping

#### Validation:
- `validate_sensor_data()` - Range checking
- `get_state_from_health()` - State mapping

#### Formatting:
- `format_timestamp()` - Unix → readable

**Design Philosophy:**
- Pure functions (no side effects)
- Comprehensive docstrings
- Type hints for clarity

---

## Data Flow Diagram

```
Arduino → Serial Port → serial_reader.py → Buffer
                             │
                             ▼
CSV File → data_replay.py → Buffer
                             │
                             ▼
                    Buffer (10 sec window)
                             │
                             ▼
                    anomaly_engine.py
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             Vibration          Temperature
             Analysis            Analysis
                    │                 │
                    └────────┬────────┘
                             ▼
                    Health Scoring
                             │
                             ▼
                    ui_components.py
                             │
                             ▼
                      Streamlit Display
```

---

## Threading Model

### Main Thread (Streamlit)
- UI rendering
- User interactions
- State management
- Display updates

### Reader Thread (Serial/Replay)
- Data acquisition
- Buffer management
- Error handling
- Statistics tracking

### Synchronization
- `threading.Lock` for buffer access
- `deque` for efficient FIFO operations
- Thread-safe `get_recent_data()`

---

## Performance Optimization

### Efficiency Measures:
1. **Deque Buffers** - O(1) append/pop
2. **Numpy Vectorization** - Fast array operations
3. **Thread Separation** - Non-blocking I/O
4. **Lazy Evaluation** - Compute only when needed
5. **Fixed Maxlen** - Automatic memory management

### Bottleneck Analysis:
- **Slowest:** Streamlit rerun (~100ms)
- **Medium:** Plotly rendering (~20ms)
- **Fastest:** Data analysis (~1ms)

### Target Performance:
- UI refresh: 5-10 FPS (achieved)
- Data ingestion: 10-20 Hz (achieved)
- Buffer size: 10 seconds (configurable)

---

## Extensibility Points

### Adding New Sensors:
1. Modify CSV format in `baseline_loader.py`
2. Add columns to `SerialReader` buffers
3. Extend `AnomalyEngine` analysis
4. Add UI components for new metrics

### Custom Algorithms:
1. Create new class inheriting `AnomalyEngine`
2. Override `analyze()` method
3. Maintain same output structure
4. Swap in `app.py`

### Alternative Data Sources:
1. Implement `get_recent_data()` interface
2. Match `SerialReader` return format
3. Provide `get_statistics()` method
4. Use duck typing in `app.py`

### UI Customization:
1. Modify `APPLE_COLORS` in `ui_components.py`
2. Adjust CSS in `apply_apple_style()`
3. Create new render functions
4. Compose in `app.py`

---

## Design Patterns Used

1. **Singleton** - Session state management
2. **Observer** - Data source monitoring
3. **Strategy** - Swappable data sources
4. **Facade** - Simplified UI components
5. **Template Method** - Analysis pipeline
6. **Factory** - Baseline loader

---

## Testing Strategy

### Unit Testing:
```python
# Test individual functions
test_compute_vibration_magnitude()
test_health_score_from_z()
test_validate_sensor_data()
```

### Integration Testing:
```python
# Test module interactions
test_baseline_loading()
test_serial_reading()
test_anomaly_detection()
```

### System Testing:
- Replay mode with known data
- Verify expected health scores
- Check UI rendering
- Monitor performance

---

## Configuration Options

### Adjustable Parameters:

**Sensitivity:**
```python
# anomaly_engine.py
self.z_caution = 2.0  # Lower = more sensitive
self.z_danger = 3.0
```

**Buffer Duration:**
```python
# serial_reader.py / data_replay.py
buffer_duration = 10.0  # seconds
```

**Analysis Window:**
```python
# app.py: render_main_dashboard()
analysis = engine.analyze(data, window_duration=2.0)
```

**UI Refresh Rate:**
```python
# app.py: main()
time.sleep(0.1)  # 10 FPS
```

---

## Security Considerations

1. **No Authentication** - Add if exposing to network
2. **Local Only** - Default to localhost:8501
3. **Input Validation** - All sensor data validated
4. **File Permissions** - CSV files should be read-only in production
5. **Serial Safety** - Auto-reconnect prevents hanging

---

## Production Deployment

### Recommended Setup:
1. Dedicated computer/Raspberry Pi
2. Reliable USB connection to Arduino
3. Auto-start on boot
4. Log rotation for diagnostics
5. Network access for remote monitoring

### Systemd Service (Linux):
```ini
[Unit]
Description=Motor Monitoring System

[Service]
WorkingDirectory=/path/to/motor_monitoring
ExecStart=/usr/local/bin/streamlit run app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Future Enhancements

Potential improvements:
1. **Data Logging** - Record all metrics to database
2. **Historical Analysis** - Trend visualization
3. **Email Alerts** - Notify on critical events
4. **Multi-Motor** - Monitor multiple motors
5. **Cloud Integration** - Remote dashboard access
6. **Predictive Maintenance** - Time-to-failure estimation
7. **Report Generation** - Automated PDF reports

---

**This architecture prioritizes interpretability, reliability, and maintainability over complexity.**









"""
Motor Preventive Monitoring System
Premium Tesla/Porsche/Apple-Style Real-Time Dashboard

Main Streamlit application for industrial motor health monitoring.
"""
import streamlit as st
import numpy as np
import time
from pathlib import Path

# Import custom modules
from baseline_loader import BaselineLoader
from serial_reader import SerialReader
from data_replay import DataReplay
from anomaly_engine import AnomalyEngine
from utils import (
    compute_vibration_magnitude_array,
    compute_rms,
    compute_coefficient_of_variation,
    compute_percentiles,
    compute_peak_to_peak,
    compute_skewness,
    compute_kurtosis
)
import ui_components as ui


# Page configuration
st.set_page_config(
    page_title="Motor Health Monitor",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.baselines = None
        st.session_state.baseline_loader = None
        st.session_state.data_source = None
        st.session_state.anomaly_engine = None
        st.session_state.current_speed = "100"
        st.session_state.mode = "replay"  # 'serial' or 'replay'
        st.session_state.last_update = time.time()


def load_baselines():
    """Load all baseline CSV files."""
    if st.session_state.baseline_loader is None:
        with st.spinner("Loading baseline profiles..."):
            try:
                data_dir = Path(__file__).parent / "data"
                loader = BaselineLoader(str(data_dir))
                baselines = loader.load_all_baselines()
                
                st.session_state.baseline_loader = loader
                st.session_state.baselines = baselines
                
                # Set initial speed to first available
                available_speeds = loader.get_available_speeds()
                if available_speeds:
                    st.session_state.current_speed = available_speeds[-1]  # Default to highest speed
                
                return True
            except Exception as e:
                st.error(f"❌ Failed to load baselines: {str(e)}")
                return False
    return True


def initialize_data_source(mode: str, **kwargs):
    """
    Initialize data source (serial or replay).
    
    Args:
        mode: 'serial' or 'replay'
        **kwargs: Additional arguments for the data source
    """
    try:
        # Stop existing source
        if st.session_state.data_source is not None:
            st.session_state.data_source.stop()
        
        if mode == "serial":
            port = kwargs.get('port', None)
            st.session_state.data_source = SerialReader(port=port)
            st.session_state.data_source.start()
            st.success(f"✅ Connected to serial port: {st.session_state.data_source.port}")
            
        elif mode == "replay":
            csv_path = kwargs.get('csv_path')
            playback_speed = kwargs.get('playback_speed', 1.0)
            st.session_state.data_source = DataReplay(
                csv_path=csv_path,
                playback_speed=playback_speed,
                loop=True
            )
            st.session_state.data_source.start()
            st.success(f"✅ Replaying data from: {Path(csv_path).name}")
        
        st.session_state.mode = mode
        return True
        
    except Exception as e:
        st.error(f"❌ Failed to initialize data source: {str(e)}")
        return False


def update_anomaly_engine(speed: str):
    """
    Update anomaly engine with new baseline.
    
    Args:
        speed: Speed percentage as string
    """
    if st.session_state.baselines and speed in st.session_state.baselines:
        baseline = st.session_state.baselines[speed]
        st.session_state.anomaly_engine = AnomalyEngine(baseline)
        st.session_state.current_speed = speed


def render_sidebar():
    """Render sidebar controls."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Mode selection
        mode = st.radio(
            "Data Source",
            ["Replay (Demo)", "Serial (Live)"],
            index=0 if st.session_state.mode == "replay" else 1
        )
        
        st.markdown("---")
        
        # Mode-specific settings
        if "Replay" in mode:
            st.markdown("### 📼 Replay Settings")
            
            # CSV file selection
            data_dir = Path(__file__).parent / "data"
            csv_files = list(data_dir.glob("*.csv"))
            csv_names = [f.name for f in csv_files]
            
            if csv_names:
                selected_csv = st.selectbox(
                    "Select CSV file",
                    csv_names,
                    index=csv_names.index("motor_100pct.csv") if "motor_100pct.csv" in csv_names else 0
                )
                
                playback_speed = st.slider(
                    "Playback Speed",
                    min_value=0.5,
                    max_value=5.0,
                    value=1.0,
                    step=0.5
                )
                
                if st.button("▶️ Start Replay", use_container_width=True):
                    csv_path = data_dir / selected_csv
                    initialize_data_source("replay", csv_path=str(csv_path), playback_speed=playback_speed)
            else:
                st.error("No CSV files found in data directory")
        
        else:
            st.markdown("### 🔌 Serial Settings")
            
            # List available ports
            available_ports = SerialReader.list_available_ports()
            
            if available_ports:
                selected_port = st.selectbox(
                    "Serial Port",
                    ["Auto-detect"] + available_ports
                )
                
                port = None if selected_port == "Auto-detect" else selected_port
                
                if st.button("🔗 Connect", use_container_width=True):
                    initialize_data_source("serial", port=port)
            else:
                st.warning("No serial ports detected")
                if st.button("🔄 Refresh Ports", use_container_width=True):
                    st.rerun()
        
        st.markdown("---")
        
        # Speed selection
        if st.session_state.baseline_loader:
            st.markdown("### 🎚️ Speed Profile")
            available_speeds = st.session_state.baseline_loader.get_available_speeds()
            
            speed_options = [f"{s}%" for s in available_speeds]
            current_option = f"{st.session_state.current_speed}%"
            
            if current_option in speed_options:
                current_index = speed_options.index(current_option)
            else:
                current_index = len(speed_options) - 1 if speed_options else 0
            
            selected = st.selectbox(
                "Baseline Speed",
                speed_options,
                index=current_index
            )
            
            new_speed = selected.replace('%', '')
            if new_speed != st.session_state.current_speed:
                update_anomaly_engine(new_speed)
                st.rerun()
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        if st.session_state.data_source:
            stats = st.session_state.data_source.get_statistics()
            
            if st.session_state.mode == "replay":
                st.metric("Packets Received", stats.get('packet_count', 0))
                st.metric("Progress", f"{stats.get('progress', 0):.0f}%")
            else:
                st.metric("FPS", f"{stats.get('fps', 0):.1f}")
                st.metric("Packets", stats.get('packet_count', 0))
                st.metric("Errors", stats.get('error_count', 0))
        
        # Restart button
        if st.button("🔄 Restart", use_container_width=True):
            if st.session_state.data_source:
                if hasattr(st.session_state.data_source, 'restart'):
                    st.session_state.data_source.restart()
                    st.success("Restarted!")


def render_main_dashboard():
    """Render main dashboard content."""
    
    # Apply premium dark theme styling
    ui.apply_premium_style()
    
    # Header
    ui.render_header(
        "Motor Health Monitor",
        "Real-time preventive monitoring for Sumitomo 3-phase induction motor"
    )
    
    # Check if we have data source
    if st.session_state.data_source is None:
        st.info("👈 Please configure and start a data source from the sidebar")
        return
    
    # Get recent data
    data = st.session_state.data_source.get_recent_data(duration=10.0)
    
    if len(data['timestamps']) == 0:
        st.info("⏳ Waiting for data...")
        return
    
    # Analyze data
    if st.session_state.anomaly_engine:
        analysis = st.session_state.anomaly_engine.analyze(data, window_duration=2.0)
    else:
        st.warning("⚠️ Anomaly engine not initialized")
        return
    
    # Get baseline for reference
    baseline = st.session_state.baselines[st.session_state.current_speed]
    
    # Status Card
    ui.render_status_card(
        analysis['overall_state'],
        analysis['overall_color'],
        analysis['messages'],
        analysis['overall_health_score']
    )
    
    ui.render_divider()
    
    # Health Gauges Row
    ui.render_section_title("Health Metrics")
    col1, col2, col3 = st.columns(3)
    
    ui.render_health_gauge(
        "Vibration Health",
        analysis['vib_health_score'],
        analysis['vib_color'],
        col=col1
    )
    
    ui.render_health_gauge(
        "Temperature Health",
        analysis['temp_health_score'],
        analysis['temp_color'],
        col=col2
    )
    
    ui.render_health_gauge(
        "Overall Health",
        analysis['overall_health_score'],
        analysis['overall_color'],
        col=col3
    )
    
    ui.render_divider()
    
    # Key Metrics - Organized in multiple rows with better spacing
    ui.render_section_title("Key Performance Indicators", "Real-time sensor metrics compared to baseline performance")
    
    # Compute additional metrics
    vib_mag = compute_vibration_magnitude_array(data['ax'], data['ay'], data['az'])
    vib_std = np.std(vib_mag) if len(vib_mag) > 0 else 0
    vib_range = np.max(vib_mag) - np.min(vib_mag) if len(vib_mag) > 0 else 0
    
    # Calculate deviation from baseline
    vib_deviation = ((analysis['vib_mean'] - baseline['vib_mean']) / baseline['vib_mean']) * 100 if baseline['vib_mean'] > 0 else 0
    temp_deviation = ((analysis['temp_mean'] - baseline['temp_mean']) / baseline['temp_mean']) * 100 if baseline['temp_mean'] > 0 else 0
    
    # Format trend indicators
    vib_trend = f"{'+' if vib_deviation >= 0 else ''}{vib_deviation:.1f}% vs baseline"
    temp_trend = f"{'+' if temp_deviation >= 0 else ''}{temp_deviation:.1f}% vs baseline"
    
    # Compute additional statistical metrics
    vib_rms = compute_rms(vib_mag) if len(vib_mag) > 0 else 0
    vib_cv = compute_coefficient_of_variation(vib_mag) if len(vib_mag) > 0 else 0
    vib_peak_to_peak = compute_peak_to_peak(vib_mag) if len(vib_mag) > 0 else 0
    vib_percentiles = compute_percentiles(vib_mag) if len(vib_mag) > 0 else {}
    vib_min = np.min(vib_mag) if len(vib_mag) > 0 else 0
    vib_skewness = compute_skewness(vib_mag) if len(vib_mag) > 0 else 0
    vib_kurtosis = compute_kurtosis(vib_mag) if len(vib_mag) > 0 else 0
    
    temp_min = np.min(data['temp']) if len(data['temp']) > 0 else 0
    temp_max = np.max(data['temp']) if len(data['temp']) > 0 else 0
    temp_range = temp_max - temp_min
    temp_cv = compute_coefficient_of_variation(data['temp']) if len(data['temp']) > 0 else 0
    
    # Row 1: Primary Vibration Metrics (5 metrics)
    vib_primary = [
        {
            'label': 'Vibration Mean',
            'value': f"{analysis['vib_mean']:.4f}",
            'unit': 'g',
            'trend': vib_trend,
            'color': ui.THEME['chart_vibration'],
            'help': 'Average vibration magnitude. Higher values may indicate bearing wear, imbalance, or misalignment.'
        },
        {
            'label': 'Vibration RMS',
            'value': f"{vib_rms:.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': 'Root Mean Square - measures overall vibration energy. More sensitive to peaks than mean.'
        },
        {
            'label': 'Std Dev',
            'value': f"{vib_std:.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': 'Standard deviation - indicates vibration consistency. High values suggest irregular motion.'
        },
        {
            'label': 'Max',
            'value': f"{analysis['vib_max']:.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': 'Maximum vibration spike detected. Sudden increases may indicate mechanical shock or failure.'
        },
        {
            'label': 'Peak-to-Peak',
            'value': f"{vib_peak_to_peak:.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': 'Range of vibration (max - min). Indicates motion amplitude and severity of oscillation.'
        }
    ]
    ui.render_metric_row(vib_primary)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Temperature Metrics (4 metrics)
    temp_metrics = [
        {
            'label': 'Temperature',
            'value': f"{analysis['temp_mean']:.1f}",
            'unit': '°C',
            'trend': temp_trend,
            'color': ui.THEME['chart_temperature'],
            'help': 'Average motor temperature. Elevated temps may indicate friction, poor lubrication, or overload.'
        },
        {
            'label': 'Temp. Range',
            'value': f"{temp_range:.1f}",
            'unit': '°C',
            'trend': None,
            'color': None,
            'help': 'Temperature variation in current window. High fluctuations may indicate unstable operation.'
        },
        {
            'label': 'Temp. Rate',
            'value': f"{analysis['temp_slope']:.3f}",
            'unit': '°C/s',
            'trend': None,
            'color': None,
            'help': 'Rate of temperature change. Rapid increases suggest developing problems or thermal runaway.'
        },
        {
            'label': 'CV (Temp)',
            'value': f"{temp_cv:.2f}",
            'unit': '%',
            'trend': None,
            'color': None,
            'help': 'Coefficient of variation - temperature stability metric. Lower is better for steady operation.'
        }
    ]
    ui.render_metric_row(temp_metrics)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 3: Statistical Indicators (4 metrics)
    statistical_indicators = [
        {
            'label': 'Z-Score (Vib)',
            'value': f"{abs(analysis['vib_z_score']):.2f}",
            'unit': 'σ',
            'trend': None,
            'color': analysis['vib_color'] if abs(analysis['vib_z_score']) > 2 else None,
            'help': 'Deviation from baseline in standard deviations. >2σ = caution, >3σ = danger.'
        },
        {
            'label': 'CV (Vib)',
            'value': f"{vib_cv:.2f}",
            'unit': '%',
            'trend': None,
            'color': None,
            'help': 'Coefficient of variation - vibration consistency. Lower values indicate steady operation.'
        },
        {
            'label': 'Skewness',
            'value': f"{vib_skewness:.3f}",
            'unit': '',
            'trend': None,
            'color': None,
            'help': 'Distribution asymmetry. Near 0 = symmetric, positive = right tail, negative = left tail.'
        },
        {
            'label': 'Kurtosis',
            'value': f"{vib_kurtosis:.3f}",
            'unit': '',
            'trend': None,
            'color': None,
            'help': 'Tail heaviness. 0 = normal, positive = heavy tails (more outliers), negative = light tails.'
        }
    ]
    ui.render_metric_row(statistical_indicators)
    
    # Additional Statistical Metrics - Percentiles
    ui.render_divider()
    ui.render_section_title("Distribution Percentiles", "Vibration magnitude distribution at key percentile thresholds")
    
    percentile_metrics = [
        {
            'label': 'P25',
            'value': f"{vib_percentiles.get('p25', 0):.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': '25th percentile - 25% of vibration readings are below this value.'
        },
        {
            'label': 'P50 (Median)',
            'value': f"{vib_percentiles.get('p50', 0):.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': 'Median - middle value. More robust to outliers than mean.'
        },
        {
            'label': 'P75',
            'value': f"{vib_percentiles.get('p75', 0):.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': '75th percentile - 75% of vibration readings are below this value.'
        },
        {
            'label': 'P95',
            'value': f"{vib_percentiles.get('p95', 0):.4f}",
            'unit': 'g',
            'trend': None,
            'color': None,
            'help': '95th percentile - captures high vibration events while excluding extreme outliers.'
        }
    ]
    
    ui.render_metric_row(percentile_metrics)
    
    ui.render_divider()
    
    # Real-Time Plots Section
    ui.render_section_title("Real-Time Sensor Data", "Live trends showing the last 10 seconds of motor operation")
    
    # Convert timestamps to relative seconds (time ago)
    if len(data['timestamps']) > 0:
        time_relative = data['timestamps'][-1] - data['timestamps']
        time_relative = time_relative[::-1]  # Reverse for "seconds ago"
        vib_mag_plot = vib_mag[::-1]
        temp_plot = data['temp'][::-1]
    else:
        time_relative = np.array([])
        vib_mag_plot = np.array([])
        temp_plot = np.array([])
    
    # Two column layout for plots
    col1, col2 = st.columns(2)
    
    with col1:
        ui.render_time_series_plot(
            time_relative,
            vib_mag_plot,
            "Vibration Magnitude",
            "Magnitude (g)",
            color=ui.THEME['chart_vibration'],
            threshold_bands={
                'normal': baseline['threshold_normal'],
                'caution': baseline['threshold_caution']
            },
            baseline_value=baseline['vib_mean']
        )
    
    with col2:
        ui.render_time_series_plot(
            time_relative,
            temp_plot,
            "Temperature Trend",
            "Temperature (°C)",
            color=ui.THEME['chart_temperature'],
            baseline_value=baseline['temp_mean']
        )
    
    # 3D Vibration Vector Visualization
    ui.render_divider()
    ui.render_section_title("3D Vibration Vector", "Current acceleration vector in three-dimensional space")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ui.render_3d_vibration_plot(
            data['ax'],
            data['ay'],
            data['az'],
            color=ui.THEME['chart_vibration']
        )
    
    with col2:
        # Individual axis metrics
        axis_metrics = [
            {
                'label': 'X-Axis',
                'value': f"{data['ax'][-1]:.4f}" if len(data['ax']) > 0 else "0.0000",
                'unit': 'g',
                'trend': None,
                'color': ui.THEME['chart_vibration']
            },
            {
                'label': 'Y-Axis',
                'value': f"{data['ay'][-1]:.4f}" if len(data['ay']) > 0 else "0.0000",
                'unit': 'g',
                'trend': None,
                'color': ui.THEME['chart_temperature']
            },
            {
                'label': 'Z-Axis',
                'value': f"{data['az'][-1]:.4f}" if len(data['az']) > 0 else "0.0000",
                'unit': 'g',
                'trend': None,
                'color': ui.THEME['accent_secondary']
            }
        ]
        
        for metric in axis_metrics:
            card_html = ui.render_metric_card(
                metric['label'],
                metric['value'],
                metric['unit'],
                metric.get('trend'),
                metric.get('color')
            )
            st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    ui.render_divider()
    
    # Statistical Distribution Plots
    ui.render_section_title("Statistical Distribution Analysis", "Frequency distributions and quartile analysis for anomaly detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ui.render_histogram_plot(
            vib_mag,
            "Vibration Magnitude Distribution",
            "Magnitude (g)",
            color=ui.THEME['chart_vibration'],
            baseline_value=baseline['vib_mean']
        )
    
    with col2:
        ui.render_box_plot(
            vib_mag,
            "Vibration Magnitude Box Plot",
            "Magnitude (g)",
            color=ui.THEME['chart_vibration'],
            baseline_value=baseline['vib_mean']
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        ui.render_histogram_plot(
            data['temp'],
            "Temperature Distribution",
            "Temperature (°C)",
            color=ui.THEME['chart_temperature'],
            baseline_value=baseline['temp_mean']
        )
    
    with col4:
        ui.render_box_plot(
            data['temp'],
            "Temperature Box Plot",
            "Temperature (°C)",
            color=ui.THEME['chart_temperature'],
            baseline_value=baseline['temp_mean']
        )
    
    ui.render_divider()
    
    # System Diagnostics
    stats = st.session_state.data_source.get_statistics()
    ui.render_diagnostics_panel(stats)
    
    # Icon Legend
    ui.render_icon_legend()


def main():
    """Main application entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Load baselines (only once)
    if not st.session_state.initialized:
        if load_baselines():
            # Initialize anomaly engine with default speed
            if st.session_state.baselines:
                update_anomaly_engine(st.session_state.current_speed)
            st.session_state.initialized = True
    
    # Render sidebar
    render_sidebar()
    
    # Render main dashboard
    render_main_dashboard()
    
    # Auto-refresh
    time.sleep(0.1)  # 10 FPS
    st.rerun()


if __name__ == "__main__":
    main()

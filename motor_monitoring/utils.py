"""
Utility functions for motor monitoring system
"""
import numpy as np
from typing import Tuple, Dict, Any
from datetime import datetime


def compute_vibration_magnitude(ax: float, ay: float, az: float) -> float:
    """
    Compute vibration magnitude from 3-axis accelerometer data.
    
    Args:
        ax, ay, az: Acceleration values in g
        
    Returns:
        Magnitude in g
    """
    return np.sqrt(ax**2 + ay**2 + az**2)


def compute_vibration_magnitude_array(ax: np.ndarray, ay: np.ndarray, az: np.ndarray) -> np.ndarray:
    """
    Compute vibration magnitude from 3-axis accelerometer arrays.
    
    Args:
        ax, ay, az: Arrays of acceleration values in g
        
    Returns:
        Array of magnitudes in g
    """
    return np.sqrt(ax**2 + ay**2 + az**2)


def compute_temperature_slope(temps: np.ndarray, timestamps: np.ndarray) -> float:
    """
    Compute temperature rate of change (°C/s) using linear regression.
    
    Args:
        temps: Array of temperatures in °C
        timestamps: Array of timestamps in seconds
        
    Returns:
        Temperature slope in °C/s
    """
    if len(temps) < 2:
        return 0.0
    
    # Normalize timestamps to start from 0
    t = timestamps - timestamps[0]
    
    # Simple linear regression
    if len(t) > 1 and np.std(t) > 0:
        slope = np.polyfit(t, temps, 1)[0]
        return slope
    return 0.0


def compute_z_score(value: float, baseline_mean: float, baseline_std: float) -> float:
    """
    Compute z-score deviation from baseline.
    
    Args:
        value: Current value
        baseline_mean: Baseline mean
        baseline_std: Baseline standard deviation
        
    Returns:
        Z-score
    """
    if baseline_std == 0:
        return 0.0
    return (value - baseline_mean) / baseline_std


def health_score_from_z(z_score: float, threshold_caution: float = 2.0, threshold_danger: float = 3.0) -> float:
    """
    Convert z-score to health score (0-100).
    
    Args:
        z_score: Absolute z-score
        threshold_caution: Z-score threshold for caution state
        threshold_danger: Z-score threshold for danger state
        
    Returns:
        Health score from 0 (critical) to 100 (perfect)
    """
    z_abs = abs(z_score)
    
    if z_abs <= threshold_caution:
        # Normal range: 100 to 70
        return max(70.0, 100.0 - (z_abs / threshold_caution) * 30.0)
    elif z_abs <= threshold_danger:
        # Caution range: 70 to 30
        progress = (z_abs - threshold_caution) / (threshold_danger - threshold_caution)
        return max(30.0, 70.0 - progress * 40.0)
    else:
        # Danger range: 30 to 0
        progress = min(1.0, (z_abs - threshold_danger) / threshold_danger)
        return max(0.0, 30.0 - progress * 30.0)


def get_state_from_health(health_score: float) -> Tuple[str, str]:
    """
    Get state label and color from health score.
    
    Args:
        health_score: Health score (0-100)
        
    Returns:
        Tuple of (state_label, color_code)
    """
    # Use theme colors (will be imported from ui_components if needed)
    if health_score >= 70:
        return "Normal", "#00FF88"  # Premium success green
    elif health_score >= 30:
        return "Caution", "#FFB800"  # Premium warning amber
    else:
        return "Danger", "#FF3366"  # Premium danger red


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted datetime string
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def validate_sensor_data(ax: float, ay: float, az: float, temp: float) -> bool:
    """
    Validate sensor data for reasonable ranges.
    
    Args:
        ax, ay, az: Acceleration values in g
        temp: Temperature in °C
        
    Returns:
        True if valid, False otherwise
    """
    # Check for NaN or infinite values
    if not all(np.isfinite([ax, ay, az, temp])):
        return False
    
    # Reasonable acceleration range: -50g to +50g
    if not all(-50 <= val <= 50 for val in [ax, ay, az]):
        return False
    
    # Reasonable temperature range: -40°C to +150°C
    if not -40 <= temp <= 150:
        return False
    
    return True


def smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply moving average smoothing to data.
    
    Args:
        data: Input data array
        window_size: Size of smoothing window
        
    Returns:
        Smoothed data array
    """
    if len(data) < window_size:
        return data
    
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='same')


def compute_rms(data: np.ndarray) -> float:
    """
    Compute Root Mean Square (RMS) value.
    
    Args:
        data: Input data array
        
    Returns:
        RMS value
    """
    if len(data) == 0:
        return 0.0
    return np.sqrt(np.mean(data**2))


def compute_coefficient_of_variation(data: np.ndarray) -> float:
    """
    Compute coefficient of variation (CV) as percentage.
    
    Args:
        data: Input data array
        
    Returns:
        Coefficient of variation as percentage
    """
    if len(data) == 0:
        return 0.0
    mean = np.mean(data)
    if mean == 0:
        return 0.0
    return (np.std(data) / mean) * 100.0


def compute_percentiles(data: np.ndarray, percentiles: list = [25, 50, 75, 95]) -> Dict[str, float]:
    """
    Compute percentiles for data.
    
    Args:
        data: Input data array
        percentiles: List of percentile values to compute
        
    Returns:
        Dictionary with percentile values
    """
    if len(data) == 0:
        return {f'p{p}': 0.0 for p in percentiles}
    
    computed = np.percentile(data, percentiles)
    return {f'p{p}': float(computed[i]) for i, p in enumerate(percentiles)}


def compute_peak_to_peak(data: np.ndarray) -> float:
    """
    Compute peak-to-peak value (max - min).
    
    Args:
        data: Input data array
        
    Returns:
        Peak-to-peak value
    """
    if len(data) == 0:
        return 0.0
    return float(np.max(data) - np.min(data))


def compute_skewness(data: np.ndarray) -> float:
    """
    Compute skewness (measure of asymmetry).
    
    Args:
        data: Input data array
        
    Returns:
        Skewness value
    """
    if len(data) < 3:
        return 0.0
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return float(np.mean(((data - mean) / std) ** 3))


def compute_kurtosis(data: np.ndarray) -> float:
    """
    Compute kurtosis (measure of tail heaviness).
    
    Args:
        data: Input data array
        
    Returns:
        Kurtosis value (excess kurtosis, so 0 = normal distribution)
    """
    if len(data) < 4:
        return 0.0
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return float(np.mean(((data - mean) / std) ** 4) - 3.0)


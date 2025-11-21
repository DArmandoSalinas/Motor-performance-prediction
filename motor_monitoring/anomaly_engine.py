"""
Anomaly Engine - Interpretable Health Scoring

Rule-based anomaly detection and health scoring for motor monitoring.
No ML, purely interpretable statistical analysis.
"""
import numpy as np
from typing import Dict, Any, List
from utils import (
    compute_vibration_magnitude_array,
    compute_temperature_slope,
    compute_z_score,
    health_score_from_z,
    get_state_from_health
)


class AnomalyEngine:
    """
    Rule-based anomaly detection engine for motor health monitoring.
    """
    
    def __init__(self, baseline: Dict[str, Any]):
        """
        Initialize anomaly engine with baseline.
        
        Args:
            baseline: Baseline statistics dictionary
        """
        self.baseline = baseline
        self.speed = baseline['speed']
        
        # Alert thresholds
        # Vibration (Even more sensitive)
        self.vib_z_caution = 1.2  # Was 1.5
        self.vib_z_danger = 2.0   # Was 2.5
        
        # Temperature (Absolute limits instead of relative)
        self.temp_min_safe = 15.0
        self.temp_max_safe = 35.0
        self.temp_tolerance = 5.0 # Tolerance beyond safe zone before danger
    
    def analyze(self, data: Dict[str, np.ndarray], window_duration: float = 2.0) -> Dict[str, Any]:
        """
        Analyze real-time data and compute health metrics.
        
        Args:
            data: Dictionary with 'timestamps', 'ax', 'ay', 'az', 'temp' arrays
            window_duration: Duration of analysis window in seconds
            
        Returns:
            Dictionary with health analysis results
        """
        # Check if we have data
        if len(data['timestamps']) == 0:
            return self._empty_result()
        
        # Get recent window
        window_data = self._get_window(data, window_duration)
        
        if len(window_data['timestamps']) < 2:
            return self._empty_result()
        
        # Compute vibration magnitude
        vib_mag = compute_vibration_magnitude_array(
            window_data['ax'],
            window_data['ay'],
            window_data['az']
        )
        
        # Vibration analysis
        vib_metrics = self._analyze_vibration(vib_mag)
        
        # Temperature analysis
        temp_metrics = self._analyze_temperature(
            window_data['temp'],
            window_data['timestamps']
        )
        
        # Overall health
        overall_health = min(vib_metrics['health_score'], temp_metrics['health_score'])
        overall_state, overall_color = get_state_from_health(overall_health)
        
        # Generate diagnostic messages
        messages = self._generate_messages(vib_metrics, temp_metrics)
        
        # Build result
        result = {
            # Vibration metrics
            'vib_mean': vib_metrics['mean'],
            'vib_std': vib_metrics['std'],
            'vib_max': vib_metrics['max'],
            'vib_z_score': vib_metrics['z_score'],
            'vib_health_score': vib_metrics['health_score'],
            'vib_state': vib_metrics['state'],
            'vib_color': vib_metrics['color'],
            
            # Temperature metrics
            'temp_mean': temp_metrics['mean'],
            'temp_std': temp_metrics['std'],
            'temp_slope': temp_metrics['slope'],
            'temp_z_score': temp_metrics['z_score'],
            'temp_health_score': temp_metrics['health_score'],
            'temp_state': temp_metrics['state'],
            'temp_color': temp_metrics['color'],
            
            # Overall
            'overall_health_score': overall_health,
            'overall_state': overall_state,
            'overall_color': overall_color,
            
            # Messages
            'messages': messages,
            'primary_message': messages[0] if messages else "No data",
            
            # Metadata
            'sample_count': len(window_data['timestamps']),
            'window_duration': window_duration,
            'baseline_speed': self.speed
        }
        
        return result
    
    def _analyze_vibration(self, vib_mag: np.ndarray) -> Dict[str, Any]:
        """
        Analyze vibration data.
        
        Args:
            vib_mag: Array of vibration magnitudes
            
        Returns:
            Dictionary with vibration metrics
        """
        # Compute statistics
        vib_mean = np.mean(vib_mag)
        vib_std = np.std(vib_mag)
        vib_max = np.max(vib_mag)
        
        # Compute z-score (deviation from baseline)
        # We check both Mean and Max deviation
        z_score_mean = compute_z_score(
            vib_mean,
            self.baseline['vib_mean'],
            self.baseline['vib_std']
        )
        
        # Use Max for impact detection (hitting the motor)
        # Since we don't have vib_max_std, we use vib_std as a proxy or check against vib_max directly
        # A sudden impact increases MAX much more than MEAN
        if self.baseline['vib_max'] > 0:
            max_ratio = vib_max / self.baseline['vib_max']
            # If current max is 2x baseline max, that's a huge impact
            # Convert ratio to pseudo z-score: (ratio - 1) * 3
            z_score_max = (max_ratio - 1.0) * 5.0
        else:
            z_score_max = 0.0
            
        # Use the worst of the two scores
        z_score = max(abs(z_score_mean), abs(z_score_max))
        
        # Compute health score
        health_score = health_score_from_z(z_score, self.vib_z_caution, self.vib_z_danger)
        
        # Get state
        state, color = get_state_from_health(health_score)
        
        return {
            'mean': vib_mean,
            'std': vib_std,
            'max': vib_max,
            'z_score': z_score,
            'health_score': health_score,
            'state': state,
            'color': color
        }
    
    def _analyze_temperature(self, temps: np.ndarray, timestamps: np.ndarray) -> Dict[str, Any]:
        """
        Analyze temperature data using absolute limits.
        
        Args:
            temps: Array of temperatures
            timestamps: Array of timestamps
            
        Returns:
            Dictionary with temperature metrics
        """
        # Compute statistics
        temp_mean = np.mean(temps)
        
        # Special handling for disconnected sensor (0 value)
        if temp_mean < 1.0:
            return {
                'mean': 0.0,
                'std': 0.0,
                'slope': 0.0,
                'z_score': 0.0,
                'z_score_mean': 0.0,
                'z_score_rate': 0.0,
                'health_score': 100.0,  # Consider healthy (ignored)
                'state': 'Sensor Off',
                'color': '#8E8E93'  # Grey
            }

        temp_std = np.std(temps)
        
        # Compute temperature slope
        temp_slope = compute_temperature_slope(temps, timestamps)
        
        # --- Absolute Limit Logic ---
        # Safe Zone: 15 - 35
        # Caution Zone: (10-15) and (35-40)
        # Danger Zone: <10 or >40
        
        health_score = 100.0
        z_score = 0.0 # Simulated Z-score for compatibility
        
        if self.temp_min_safe <= temp_mean <= self.temp_max_safe:
            # Perfect zone
            health_score = 100.0
            z_score = 0.5 # Low z-score
        else:
            # Outside safe zone
            if temp_mean > self.temp_max_safe:
                excess = temp_mean - self.temp_max_safe
                if excess <= self.temp_tolerance:
                    # Caution zone (e.g. 35-40)
                    # Linear drop from 100 to 50
                    health_score = 100.0 - (excess / self.temp_tolerance) * 50.0
                    z_score = 2.5 # Caution level
                else:
                    # Danger zone (>40)
                    health_score = 0.0
                    z_score = 5.0 # Danger level
            
            elif temp_mean < self.temp_min_safe:
                deficit = self.temp_min_safe - temp_mean
                if deficit <= self.temp_tolerance:
                    # Caution zone (e.g. 10-15)
                    health_score = 100.0 - (deficit / self.temp_tolerance) * 50.0
                    z_score = 2.5
                else:
                    # Danger zone (<10)
                    health_score = 0.0
                    z_score = 5.0
        
        # Ensure bounds
        health_score = max(0.0, min(100.0, health_score))
        
        # Get state
        state, color = get_state_from_health(health_score)
        
        return {
            'mean': temp_mean,
            'std': temp_std,
            'slope': temp_slope,
            'z_score': z_score, # Simulated
            'z_score_mean': z_score,
            'z_score_rate': 0.0,
            'health_score': health_score,
            'state': state,
            'color': color
        }
    
    def _generate_messages(self, vib_metrics: Dict, temp_metrics: Dict) -> List[str]:
        """
        Generate human-readable diagnostic messages.
        
        Args:
            vib_metrics: Vibration analysis results
            temp_metrics: Temperature analysis results
            
        Returns:
            List of diagnostic messages
        """
        messages = []
        
        # Vibration messages
        vib_z = vib_metrics['z_score']
        if abs(vib_z) <= self.vib_z_caution:
            messages.append("✅ Vibration within normal range")
        elif abs(vib_z) <= self.vib_z_danger:
            if vib_z > 0:
                messages.append("⚠️ Vibration elevated above normal")
            else:
                messages.append("⚠️ Vibration unusually low")
        else:
            if vib_z > 0:
                messages.append("🚨 High vibration detected!")
            else:
                messages.append("🚨 Abnormally low vibration!")
        
        # Temperature messages (Absolute limits)
        temp_mean = temp_metrics['mean']
        
        if temp_mean < 1.0:
             messages.append("⚪ Temperature sensor disconnected")
        elif self.temp_min_safe <= temp_mean <= self.temp_max_safe:
            messages.append(f"✅ Temperature optimal ({temp_mean:.1f}°C)")
        else:
            if temp_mean > self.temp_max_safe:
                excess = temp_mean - self.temp_max_safe
                if excess <= self.temp_tolerance:
                    messages.append(f"⚠️ Temperature slightly high ({temp_mean:.1f}°C)")
                else:
                    messages.append(f"🚨 Temperature CRITICAL HIGH ({temp_mean:.1f}°C)!")
            elif temp_mean < self.temp_min_safe:
                deficit = self.temp_min_safe - temp_mean
                if deficit <= self.temp_tolerance:
                    messages.append(f"⚠️ Temperature slightly low ({temp_mean:.1f}°C)")
                else:
                    messages.append(f"🚨 Temperature CRITICAL LOW ({temp_mean:.1f}°C)!")
        
        # Overall health message
        overall_health = min(vib_metrics['health_score'], temp_metrics['health_score'])
        
        if overall_health >= 90:
            messages.append("💚 Motor operating in excellent condition")
        elif overall_health >= 70:
            messages.append("💚 Motor operating normally")
        elif overall_health >= 50:
            messages.append("⚠️ Minor deviations detected - monitor closely")
        elif overall_health >= 30:
            messages.append("⚠️ Caution - significant deviations from baseline")
        else:
            messages.append("🚨 Critical - immediate inspection recommended!")
        
        return messages
    
    def _get_window(self, data: Dict[str, np.ndarray], duration: float) -> Dict[str, np.ndarray]:
        """
        Extract most recent window from data.
        
        Args:
            data: Full data dictionary
            duration: Window duration in seconds
            
        Returns:
            Windowed data dictionary
        """
        if len(data['timestamps']) == 0:
            return data
        
        cutoff = data['timestamps'][-1] - duration
        mask = data['timestamps'] >= cutoff
        
        return {
            'timestamps': data['timestamps'][mask],
            'ax': data['ax'][mask],
            'ay': data['ay'][mask],
            'az': data['az'][mask],
            'temp': data['temp'][mask]
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """
        Return empty result when no data is available.
        
        Returns:
            Dictionary with default values
        """
        return {
            'vib_mean': 0.0,
            'vib_std': 0.0,
            'vib_max': 0.0,
            'vib_z_score': 0.0,
            'vib_health_score': 100.0,
            'vib_state': 'No Data',
            'vib_color': '#8E8E93',  # Apple Gray
            
            'temp_mean': 0.0,
            'temp_std': 0.0,
            'temp_slope': 0.0,
            'temp_z_score': 0.0,
            'temp_health_score': 100.0,
            'temp_state': 'No Data',
            'temp_color': '#8E8E93',
            
            'overall_health_score': 100.0,
            'overall_state': 'No Data',
            'overall_color': '#8E8E93',
            
            'messages': ['Waiting for data...'],
            'primary_message': 'Waiting for data...',
            
            'sample_count': 0,
            'window_duration': 0.0,
            'baseline_speed': self.speed
        }




"""
Baseline Loader - Multi-speed Normal Profile Engine

Loads baseline CSV files for different motor speeds and computes statistical signatures.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Any
from utils import compute_vibration_magnitude_array


class BaselineLoader:
    """
    Loads and processes baseline CSV files for multiple motor speeds.
    """
    
    def __init__(self, data_dir: str = "data", machine_type: str = "sumitomo"):
        """
        Initialize the baseline loader.
        
        Args:
            data_dir: Base directory containing machine-specific subdirectories
            machine_type: Type of machine ("sumitomo" or "haas")
        """
        self.data_dir = data_dir
        self.machine_type = machine_type
        self.baselines = {}
        
        # Different speed configurations for different machines
        if machine_type == "sumitomo":
            self.speeds = ["50", "60", "75", "90", "100"]
            self.machine_dir = "sumitomo"
        elif machine_type == "haas":
            self.speeds = ["baseline"]  # Haas uses trajectory-based baselines
            self.machine_dir = "haas"
        else:
            raise ValueError(f"Unknown machine type: {machine_type}")
        
    def load_all_baselines(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all baseline CSV files and compute statistical signatures.
        
        Returns:
            Dictionary mapping speed percentages to baseline statistics
        """
        machine_data_dir = os.path.join(self.data_dir, self.machine_dir)
        
        if self.machine_type == "sumitomo":
            # Sumitomo: Load speed-based baselines
            for speed in self.speeds:
                csv_path = os.path.join(machine_data_dir, f"motor_{speed}pct.csv")
                
                if not os.path.exists(csv_path):
                    print(f"⚠️  Warning: Baseline file not found: {csv_path}")
                    continue
                
                try:
                    baseline = self._load_baseline(csv_path, speed)
                    self.baselines[speed] = baseline
                    print(f"✅ Loaded baseline for {speed}% speed")
                except Exception as e:
                    print(f"❌ Error loading {csv_path}: {str(e)}")
        
        elif self.machine_type == "haas":
            # Haas: Load trajectory-based baseline (combine all good trajectories)
            # First, try to find a combined baseline file
            baseline_path = os.path.join(machine_data_dir, "haas_baseline.csv")
            
            if os.path.exists(baseline_path):
                # Use pre-computed baseline
                try:
                    baseline = self._load_baseline(baseline_path, "baseline")
                    self.baselines["baseline"] = baseline
                    print(f"✅ Loaded Haas baseline from {baseline_path}")
                except Exception as e:
                    print(f"❌ Error loading {baseline_path}: {str(e)}")
            else:
                # Create baseline from ALL available CSV files (combining all trajectories)
                csv_files = sorted([f for f in os.listdir(machine_data_dir) if f.endswith('.csv')])
                if csv_files:
                    print(f"📊 Creating Haas baseline from ALL {len(csv_files)} trajectory files...")
                    print(f"   Files: {', '.join(csv_files[:5])}{'...' if len(csv_files) > 5 else ''}")
                    try:
                        baseline = self._load_combined_baseline(machine_data_dir, csv_files)
                        self.baselines["baseline"] = baseline
                        print(f"✅ Created Haas baseline from {len(csv_files)} files ({baseline['sample_count']} total samples)")
                    except Exception as e:
                        print(f"❌ Error creating baseline: {str(e)}")
        
        if not self.baselines:
            raise ValueError(f"No baseline files could be loaded for {self.machine_type}!")
        
        return self.baselines
    
    def _load_baseline(self, csv_path: str, speed: str) -> Dict[str, Any]:
        """
        Load a single baseline CSV and compute statistics.
        
        Args:
            csv_path: Path to CSV file
            speed: Speed percentage as string
            
        Returns:
            Dictionary with baseline statistics
        """
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Use the DataFrame-based method
        return self._load_baseline_from_df(df, speed)
    
    def _load_combined_baseline(self, data_dir: str, csv_files: list) -> Dict[str, Any]:
        """
        Load and combine ALL CSV files into a single baseline.
        This combines all trajectory data to create a comprehensive baseline profile.
        
        Args:
            data_dir: Directory containing CSV files
            csv_files: List of CSV filenames to combine (all files will be used)
            
        Returns:
            Combined baseline dictionary
        """
        all_dfs = []
        loaded_count = 0
        
        for csv_file in csv_files:
            csv_path = os.path.join(data_dir, csv_file)
            try:
                df = pd.read_csv(csv_path)
                required_cols = ['timestamp', 'ax_g', 'ay_g', 'az_g', 'temp_C']
                if all(col in df.columns for col in required_cols):
                    all_dfs.append(df)
                    loaded_count += 1
                else:
                    print(f"⚠️  Warning: {csv_file} missing required columns, skipping")
            except Exception as e:
                print(f"⚠️  Warning: Could not load {csv_file}: {str(e)}")
        
        if not all_dfs:
            raise ValueError("No valid CSV files found to create baseline")
        
        print(f"   ✓ Loaded {loaded_count}/{len(csv_files)} files successfully")
        
        # Combine all dataframes into one comprehensive dataset
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
        
        print(f"   ✓ Combined {len(combined_df)} total samples from all trajectories")
        
        # Use the combined data to create baseline
        return self._load_baseline_from_df(combined_df, "baseline")
    
    def _load_baseline_from_df(self, df: pd.DataFrame, speed: str) -> Dict[str, Any]:
        """
        Create baseline from a DataFrame (used internally).
        
        Args:
            df: DataFrame with sensor data
            speed: Speed/trajectory identifier
            
        Returns:
            Baseline dictionary
        """
        # Validate required columns
        required_cols = ['timestamp', 'ax_g', 'ay_g', 'az_g', 'temp_C']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Extract data
        timestamps = df['timestamp'].values
        ax = df['ax_g'].values
        ay = df['ay_g'].values
        az = df['az_g'].values
        temps = df['temp_C'].values
        
        # Compute vibration magnitude
        vib_mag = compute_vibration_magnitude_array(ax, ay, az)
        
        # Compute sampling rate
        if len(timestamps) > 1:
            time_diffs = np.diff(timestamps)
            sampling_rate = 1.0 / np.mean(time_diffs) if np.mean(time_diffs) > 0 else 10.0
        else:
            sampling_rate = 10.0
        
        # Vibration statistics
        vib_mean = np.mean(vib_mag)
        vib_std = np.std(vib_mag)
        vib_min = np.min(vib_mag)
        vib_max = np.max(vib_mag)
        vib_median = np.median(vib_mag)
        vib_percentile_95 = np.percentile(vib_mag, 95)
        
        # Temperature statistics
        temp_mean = np.mean(temps)
        temp_std = np.std(temps)
        temp_min = np.min(temps)
        temp_max = np.max(temps)
        temp_median = np.median(temps)
        
        # Temperature rate of change (simple approach)
        if len(temps) > 10:
            temp_diffs = np.diff(temps)
            time_diffs = np.diff(timestamps)
            # Avoid division by zero
            valid_mask = time_diffs > 0
            if np.any(valid_mask):
                temp_rates = temp_diffs[valid_mask] / time_diffs[valid_mask]
                temp_rate_mean = np.mean(temp_rates)
                temp_rate_std = np.std(temp_rates) if len(temp_rates) > 1 else 0.0
            else:
                temp_rate_mean = 0.0
                temp_rate_std = 0.0
        else:
            temp_rate_mean = 0.0
            temp_rate_std = 0.0
        
        # Compute threshold bands
        threshold_normal = vib_mean + 2 * vib_std
        threshold_caution = vib_mean + 3 * vib_std
        
        # Build baseline dictionary
        baseline = {
            "speed": speed,
            "sample_count": len(df),
            "duration_sec": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            "sampling_rate_hz": sampling_rate,
            
            # Vibration statistics
            "vib_mean": vib_mean,
            "vib_std": vib_std,
            "vib_min": vib_min,
            "vib_max": vib_max,
            "vib_median": vib_median,
            "vib_percentile_95": vib_percentile_95,
            "vib_range": vib_max - vib_min,
            
            # Thresholds
            "threshold_normal": threshold_normal,
            "threshold_caution": threshold_caution,
            
            # Temperature statistics
            "temp_mean": temp_mean,
            "temp_std": temp_std,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "temp_median": temp_median,
            
            # Temperature rate
            "temp_rate_mean": temp_rate_mean,
            "temp_rate_std": temp_rate_std,
            
            # Raw data (for visualization if needed)
            "vib_mag_array": vib_mag,
            "temp_array": temps,
            "timestamp_array": timestamps
        }
        
        return baseline
    
    def get_baseline(self, speed: str) -> Dict[str, Any]:
        """
        Get baseline for a specific speed.
        
        Args:
            speed: Speed percentage as string ("50", "60", etc.)
            
        Returns:
            Baseline dictionary
        """
        if speed not in self.baselines:
            raise ValueError(f"Baseline for speed {speed}% not loaded")
        return self.baselines[speed]
    
    def get_available_speeds(self) -> list:
        """
        Get list of available speed baselines.
        
        Returns:
            List of speed percentage strings
        """
        return list(self.baselines.keys())
    
    def print_summary(self):
        """
        Print a summary of all loaded baselines.
        """
        print("\n" + "="*70)
        print("BASELINE SUMMARY")
        print("="*70)
        
        for speed in sorted(self.baselines.keys(), key=lambda x: int(x)):
            baseline = self.baselines[speed]
            print(f"\n🔧 Speed: {speed}%")
            print(f"   Samples: {baseline['sample_count']}")
            print(f"   Duration: {baseline['duration_sec']:.1f} sec")
            print(f"   Sampling Rate: {baseline['sampling_rate_hz']:.1f} Hz")
            print(f"   Vibration: {baseline['vib_mean']:.4f} ± {baseline['vib_std']:.4f} g")
            print(f"   Normal Threshold: {baseline['threshold_normal']:.4f} g")
            print(f"   Caution Threshold: {baseline['threshold_caution']:.4f} g")
            print(f"   Temperature: {baseline['temp_mean']:.2f} ± {baseline['temp_std']:.2f} °C")
        
        print("\n" + "="*70 + "\n")


# Convenience function
def load_baselines(data_dir: str = "data") -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to load all baselines.
    
    Args:
        data_dir: Directory containing baseline CSV files
        
    Returns:
        Dictionary of baselines
    """
    loader = BaselineLoader(data_dir)
    return loader.load_all_baselines()









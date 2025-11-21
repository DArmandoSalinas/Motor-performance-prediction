"""
Data Replay - CSV Simulation Mode

Replays CSV data as if it were real-time sensor input (for demo without hardware).
"""
import pandas as pd
import numpy as np
import threading
import time
from collections import deque
from typing import Optional, Dict, Any
from utils import validate_sensor_data


class DataReplay:
    """
    Replays CSV data to simulate real-time sensor input.
    """
    
    def __init__(self, csv_path: str, playback_speed: float = 1.0, loop: bool = True):
        """
        Initialize data replay.
        
        Args:
            csv_path: Path to CSV file to replay
            playback_speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x speed)
            loop: Whether to loop the data continuously
        """
        self.csv_path = csv_path
        self.playback_speed = playback_speed
        self.loop = loop
        
        # Load CSV data
        self.df = pd.read_csv(csv_path)
        self._validate_csv()
        
        # Threading
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.Lock()
        
        # Data buffers (matching SerialReader interface)
        self.timestamps = deque(maxlen=10000)
        self.ax_buffer = deque(maxlen=10000)
        self.ay_buffer = deque(maxlen=10000)
        self.az_buffer = deque(maxlen=10000)
        self.temp_buffer = deque(maxlen=10000)
        
        # Replay state
        self.current_index = 0
        self.start_time = None
        self.data_start_time = None
        
        # Statistics
        self.packet_count = 0
        self.buffer_duration = 10.0
        
        print(f"📼 Loaded {len(self.df)} samples from {csv_path}")
    
    def _validate_csv(self):
        """
        Validate CSV has required columns.
        """
        required_cols = ['timestamp', 'ax_g', 'ay_g', 'az_g', 'temp_C']
        if not all(col in self.df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
    
    def start(self):
        """
        Start replay thread.
        """
        if self.running:
            print("⚠️  Replay already running")
            return
        
        self.running = True
        self.start_time = time.time()
        self.data_start_time = self.df['timestamp'].iloc[0]
        self.current_index = 0
        
        self.thread = threading.Thread(target=self._replay_loop, daemon=True)
        self.thread.start()
        print("▶️  Data replay started")
    
    def stop(self):
        """
        Stop replay thread.
        """
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        print("⏹️  Data replay stopped")
    
    def _replay_loop(self):
        """
        Main replay loop (runs in separate thread).
        """
        while self.running:
            try:
                # Check if we've reached the end
                if self.current_index >= len(self.df):
                    if self.loop:
                        print("🔄 Looping replay...")
                        self.current_index = 0
                        self.start_time = time.time()
                    else:
                        print("⏹️  Replay finished")
                        self.running = False
                        break
                
                # Get current data row
                row = self.df.iloc[self.current_index]
                
                # Calculate when this data point should be sent
                data_time = row['timestamp']
                elapsed_data_time = (data_time - self.data_start_time) / self.playback_speed
                target_time = self.start_time + elapsed_data_time
                
                # Wait until target time
                current_time = time.time()
                if current_time < target_time:
                    time.sleep(target_time - current_time)
                
                # Extract data
                timestamp = time.time()  # Use current time for simulated real-time
                ax = float(row['ax_g'])
                ay = float(row['ay_g'])
                az = float(row['az_g'])
                temp = float(row['temp_C'])
                
                # Validate and add data
                if validate_sensor_data(ax, ay, az, temp):
                    self._add_data_point(timestamp, ax, ay, az, temp)
                
                self.current_index += 1
                
            except Exception as e:
                print(f"⚠️  Replay error: {str(e)}")
                time.sleep(0.1)
    
    def _add_data_point(self, timestamp: float, ax: float, ay: float, az: float, temp: float):
        """
        Add data point to buffers.
        
        Args:
            timestamp: Unix timestamp
            ax, ay, az: Acceleration in g
            temp: Temperature in °C
        """
        with self.lock:
            # Add to buffers
            self.timestamps.append(timestamp)
            self.ax_buffer.append(ax)
            self.ay_buffer.append(ay)
            self.az_buffer.append(az)
            self.temp_buffer.append(temp)
            
            self.packet_count += 1
            
            # Trim old data
            self._trim_old_data(timestamp)
    
    def _trim_old_data(self, current_timestamp: float):
        """
        Remove data older than buffer_duration.
        
        Args:
            current_timestamp: Current timestamp
        """
        cutoff_time = current_timestamp - self.buffer_duration
        
        while self.timestamps and self.timestamps[0] < cutoff_time:
            self.timestamps.popleft()
            self.ax_buffer.popleft()
            self.ay_buffer.popleft()
            self.az_buffer.popleft()
            self.temp_buffer.popleft()
    
    def get_recent_data(self, duration: float = None) -> Dict[str, np.ndarray]:
        """
        Get recent data from buffer (matching SerialReader interface).
        
        Args:
            duration: Duration in seconds (None = all buffered data)
            
        Returns:
            Dictionary with arrays of timestamps, ax, ay, az, temp
        """
        with self.lock:
            if not self.timestamps:
                return {
                    'timestamps': np.array([]),
                    'ax': np.array([]),
                    'ay': np.array([]),
                    'az': np.array([]),
                    'temp': np.array([])
                }
            
            timestamps = np.array(self.timestamps)
            ax = np.array(self.ax_buffer)
            ay = np.array(self.ay_buffer)
            az = np.array(self.az_buffer)
            temp = np.array(self.temp_buffer)
            
            if duration is not None and len(timestamps) > 0:
                cutoff = timestamps[-1] - duration
                mask = timestamps >= cutoff
                timestamps = timestamps[mask]
                ax = ax[mask]
                ay = ay[mask]
                az = az[mask]
                temp = temp[mask]
            
            return {
                'timestamps': timestamps,
                'ax': ax,
                'ay': ay,
                'az': az,
                'temp': temp
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get replay statistics (matching SerialReader interface).
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            buffer_size = len(self.timestamps)
            buffer_duration_actual = 0.0
            if len(self.timestamps) > 1:
                buffer_duration_actual = self.timestamps[-1] - self.timestamps[0]
            
            progress = (self.current_index / len(self.df)) * 100 if len(self.df) > 0 else 0
        
        return {
            'mode': 'replay',
            'source': self.csv_path,
            'packet_count': self.packet_count,
            'buffer_size': buffer_size,
            'buffer_duration': buffer_duration_actual,
            'progress': progress,
            'playback_speed': self.playback_speed,
            'looping': self.loop
        }
    
    def set_playback_speed(self, speed: float):
        """
        Change playback speed.
        
        Args:
            speed: New playback speed multiplier
        """
        self.playback_speed = max(0.1, min(10.0, speed))
        print(f"⏩ Playback speed set to {self.playback_speed}x")
    
    def restart(self):
        """
        Restart replay from beginning.
        """
        was_running = self.running
        
        if was_running:
            self.stop()
        
        # Clear buffers
        with self.lock:
            self.timestamps.clear()
            self.ax_buffer.clear()
            self.ay_buffer.clear()
            self.az_buffer.clear()
            self.temp_buffer.clear()
            self.packet_count = 0
        
        if was_running:
            self.start()
        
        print("🔄 Replay restarted")






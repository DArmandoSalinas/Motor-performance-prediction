"""
Serial Reader - Robust Threaded Serial Ingestion

Reads real-time sensor data from Arduino via serial port.
"""
import serial
import serial.tools.list_ports
import threading
import time
import queue
from collections import deque
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from utils import validate_sensor_data


class SerialReader:
    """
    Threaded serial port reader for real-time sensor data.
    """
    
    def __init__(self, port: str = None, baud_rate: int = 115200, buffer_duration: float = 10.0):
        """
        Initialize the serial reader.
        
        Args:
            port: Serial port name (e.g., 'COM4', '/dev/ttyUSB0'). If None, auto-detect.
            baud_rate: Baud rate for serial communication
            buffer_duration: Duration of rolling buffer in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.buffer_duration = buffer_duration
        
        # Serial connection
        self.serial_conn: Optional[serial.Serial] = None
        self.connected = False
        
        # Threading
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.Lock()
        
        # Data buffers (using deque for efficient append/pop)
        self.timestamps = deque(maxlen=10000)
        self.ax_buffer = deque(maxlen=10000)
        self.ay_buffer = deque(maxlen=10000)
        self.az_buffer = deque(maxlen=10000)
        self.temp_buffer = deque(maxlen=10000)
        
        # Statistics
        self.packet_count = 0
        self.error_count = 0
        self.dropped_packets = 0
        self.last_packet_time = 0
        self.fps = 0.0
        self.fps_samples = deque(maxlen=30)
        
    def auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect Arduino serial port.
        
        Returns:
            Port name if found, None otherwise
        """
        ports = serial.tools.list_ports.comports()
        
        # Look for common Arduino identifiers
        arduino_keywords = ['Arduino', 'CH340', 'USB Serial', 'FTDI', 'USB-SERIAL']
        
        for port in ports:
            description = port.description.upper()
            manufacturer = (port.manufacturer or "").upper()
            
            for keyword in arduino_keywords:
                if keyword.upper() in description or keyword.upper() in manufacturer:
                    print(f"🔍 Auto-detected Arduino on: {port.device}")
                    return port.device
        
        # If no match, just return first available port
        if ports:
            print(f"⚠️  No Arduino detected, using first available port: {ports[0].device}")
            return ports[0].device
        
        return None
    
    def connect(self) -> bool:
        """
        Connect to serial port.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            # Auto-detect port if not specified
            if self.port is None:
                self.port = self.auto_detect_port()
                if self.port is None:
                    print("❌ No serial ports found")
                    return False
            
            # Open serial connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1.0,
                write_timeout=1.0
            )
            
            # Wait for connection to stabilize
            time.sleep(2.0)
            
            # Flush any initial garbage data
            self.serial_conn.reset_input_buffer()
            
            self.connected = True
            print(f"✅ Connected to {self.port} at {self.baud_rate} baud")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Disconnect from serial port.
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            print("🔌 Disconnected from serial port")
    
    def start(self):
        """
        Start reading thread.
        """
        if self.running:
            print("⚠️  Reader already running")
            return
        
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Could not connect to serial port")
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print("▶️  Serial reader started")
    
    def stop(self):
        """
        Stop reading thread.
        """
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        self.disconnect()
        print("⏹️  Serial reader stopped")
    
    def _read_loop(self):
        """
        Main reading loop (runs in separate thread).
        """
        while self.running:
            try:
                # Read line from serial
                if not self.serial_conn or not self.serial_conn.is_open:
                    # Try to reconnect
                    print("⚠️  Connection lost, attempting reconnect...")
                    time.sleep(1.0)
                    if not self.connect():
                        time.sleep(2.0)
                        continue
                
                # Read and decode line
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                
                if not line:
                    continue
                
                # Skip header line if present (Arduino sends "ax_g,ay_g,az_g,temp_C")
                if line.lower().startswith('ax_g') or line.lower().startswith('timestamp'):
                    continue
                
                # Parse data
                data = self._parse_line(line)
                if data is not None:
                    self._add_data_point(*data)
                    
            except serial.SerialException as e:
                print(f"⚠️  Serial error: {str(e)}")
                self.error_count += 1
                self.connected = False
                time.sleep(1.0)
                
            except Exception as e:
                print(f"⚠️  Unexpected error: {str(e)}")
                self.error_count += 1
                time.sleep(0.1)
    
    def _parse_line(self, line: str) -> Optional[Tuple[float, float, float, float, float]]:
        """
        Parse CSV line: ax_g,ay_g,az_g,temp_C (Arduino format)
        OR timestamp,ax_g,ay_g,az_g,temp_C (if timestamp included)
        
        Automatically adds timestamp if not present (like data collection script).
        
        Args:
            line: CSV line string
            
        Returns:
            Tuple of (timestamp, ax, ay, az, temp) or None if invalid
        """
        try:
            parts = line.split(',')
            
            # Check if timestamp is already included (5 parts) or not (4 parts)
            if len(parts) == 5:
                # Format: timestamp,ax_g,ay_g,az_g,temp_C
                timestamp = float(parts[0])
                ax = float(parts[1])
                ay = float(parts[2])
                az = float(parts[3])
                temp = float(parts[4])
            elif len(parts) == 4:
                # Format: ax_g,ay_g,az_g,temp_C (Arduino format)
                # Add timestamp immediately when data is received (most accurate)
                timestamp = time.time()
                ax = float(parts[0])
                ay = float(parts[1])
                az = float(parts[2])
                temp = float(parts[3])
            else:
                return None
            
            # Validate data
            if not validate_sensor_data(ax, ay, az, temp):
                self.dropped_packets += 1
                return None
            
            return (timestamp, ax, ay, az, temp)
            
        except (ValueError, IndexError):
            self.error_count += 1
            return None
    
    def _add_data_point(self, timestamp: float, ax: float, ay: float, az: float, temp: float):
        """
        Add data point to buffers with thread safety.
        
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
            
            # Update statistics
            self.packet_count += 1
            current_time = time.time()
            
            if self.last_packet_time > 0:
                dt = current_time - self.last_packet_time
                if dt > 0:
                    self.fps_samples.append(1.0 / dt)
                    self.fps = np.mean(list(self.fps_samples))
            
            self.last_packet_time = current_time
            
            # Trim old data (keep only buffer_duration seconds)
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
        Get recent data from buffer.
        
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
        Get reader statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            buffer_size = len(self.timestamps)
            buffer_duration_actual = 0.0
            if len(self.timestamps) > 1:
                buffer_duration_actual = self.timestamps[-1] - self.timestamps[0]
        
        return {
            'connected': self.connected,
            'port': self.port,
            'packet_count': self.packet_count,
            'error_count': self.error_count,
            'dropped_packets': self.dropped_packets,
            'fps': self.fps,
            'buffer_size': buffer_size,
            'buffer_duration': buffer_duration_actual
        }
    
    @staticmethod
    def list_available_ports() -> List[str]:
        """
        List all available serial ports.
        
        Returns:
            List of port names
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]



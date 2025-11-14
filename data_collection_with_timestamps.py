"""
Enhanced Motor Data Collection Script with Timestamps
======================================================
Collects sensor data from Arduino and saves with Unix timestamps (seconds since epoch).
This format is compact and optimal for feature extraction and time-series analysis.
"""

import serial
import time
import datetime
import os
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================
SERIAL_PORT = 'COM4'  # Change to your Arduino port (use 'ls /dev/tty.*' on Mac/Linux)
BAUD_RATE = 460800  # Increased for 500 Hz sampling (was 115200)
# BANDWIDTH CALCULATION:
# - 500 Hz × ~55 bytes/reading = ~27,500 bytes/sec needed
# - 115200 baud = ~11,520 bytes/sec (INSUFFICIENT ❌)
# - 460800 baud = ~46,080 bytes/sec (SUFFICIENT ✅)
# - 921600 baud = ~92,160 bytes/sec (more than enough, but may be unstable)
# NOTE: Verify your Arduino supports 460800 baud (most modern ones do)

SAMPLING_INTERVAL = 0.002  # seconds between readings (0 for as fast as possible)
# CURRENT: 0.002s = 500 Hz - Detailed fault analysis
# RECOMMENDED VALUES:
# - Detailed fault analysis: 0.002-0.005 (200-500 Hz) - CURRENT SETTING ✅
# - General monitoring: 0.01-0.02 (50-100 Hz) - requires 115200 baud
# - Basic monitoring: 0.05-0.1 (10-20 Hz) - requires 115200 baud
# - Temperature trends: 0.1-1.0 (1-10 Hz) - requires 115200 baud
# NOTE: 500 Hz captures frequencies up to 250 Hz (Nyquist), excellent for bearing defects

# ============================================================================
# SETUP
# ============================================================================
def setup_data_collection():
    """Initialize serial connection and create output file"""
    
    # Create filename with date and time
    now = datetime.datetime.now()
    filename = now.strftime("motor_data_%Y%m%d_%H%M%S.csv")
    
    print("="*70)
    print(" MOTOR DATA COLLECTION - STARTED")
    print("="*70)
    print(f"📁 Output file: {filename}")
    print(f"🔌 Serial port: {SERIAL_PORT}")
    print(f"⚡ Baud rate: {BAUD_RATE}")
    print(f"⏱️  Sampling interval: {SAMPLING_INTERVAL}s")
    print("="*70)
    print("\n⚠️  IMPORTANT: Make sure Arduino/ESP32 is running first!")
    print("   The Arduino code must be uploaded and running before starting this script.")
    print("\nPress Ctrl+C to stop collection\n")
    
    # Initialize serial connection
    try:
        print("🔌 Connecting to Arduino...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✓ Serial connection established")
        
        # Clear any buffered data
        ser.reset_input_buffer()
        time.sleep(0.5)
        
        # Verify Arduino is sending data
        print("⏳ Waiting for data from Arduino...")
        wait_start = time.time()
        while ser.in_waiting == 0:
            if time.time() - wait_start > 5:
                print("⚠️  WARNING: No data received from Arduino after 5 seconds")
                print("   Make sure:")
                print("   1. Arduino code is uploaded and running")
                print("   2. Baud rate matches (should be 460800)")
                print("   3. Arduino is sending data in format: ax_g,ay_g,az_g,temp_C")
                break
            time.sleep(0.1)
        
        if ser.in_waiting > 0:
            print("✓ Arduino is sending data!\n")
        else:
            print("⚠️  Proceeding anyway, but Arduino may not be ready\n")
            
    except Exception as e:
        print(f"❌ Error connecting to serial port: {e}")
        print(f"\n   Troubleshooting:")
        print(f"   1. Make sure Arduino/ESP32 is connected to {SERIAL_PORT}")
        print(f"   2. Upload and run the Arduino code first")
        print(f"   3. Check if the port name is correct (use 'ls /dev/tty.*' on Mac/Linux)")
        print(f"   4. Close any other programs using the serial port (Arduino IDE Serial Monitor)")
        sys.exit(1)
    
    return ser, filename

# ============================================================================
# DATA COLLECTION LOOP
# ============================================================================
def collect_data():
    """Main data collection loop"""
    
    ser, filename = setup_data_collection()
    
    try:
        with open(filename, 'w') as file:
            # Write CSV header
            file.write("timestamp,ax_g,ay_g,az_g,temp_C\n")
            
            reading_count = 0
            error_count = 0
            start_time = time.time()
            
            print("📊 Collecting data...\n")
            
            while True:
                if ser.in_waiting > 0:
                    try:
                        # Read data from Arduino first
                        data = ser.readline().decode('utf-8').strip()
                        
                        # Capture timestamp IMMEDIATELY after reading data
                        # Use time.time() which provides microsecond precision (float)
                        # This ensures timestamp reflects the exact moment data was received
                        timestamp = time.time()
                        
                        # Validate data
                        if not data or ',' not in data:
                            error_count += 1
                            continue
                        
                        # Check if data has correct number of columns (4 values expected: ax, ay, az, temp)
                        data_parts = data.split(',')
                        if len(data_parts) != 4:
                            print(f"⚠️  Malformed data (expected 4 values, got {len(data_parts)}): {data}")
                            error_count += 1
                            continue
                        
                        # Write timestamped data with sufficient decimal precision
                        # Use .9f format to preserve microsecond precision (9 decimal places)
                        # This ensures we can distinguish readings at 500 Hz (0.002s intervals)
                        full_data = f"{timestamp:.9f},{data}"
                        file.write(full_data + '\n')
                        file.flush()  # Force write to disk
                        
                        reading_count += 1
                        
                        # Print progress every 10 readings
                        if reading_count % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = reading_count / elapsed if elapsed > 0 else 0
                            print(f"✓ Reading #{reading_count:4d} | Rate: {rate:.1f} Hz | Latest: {data}")
                        
                        # Control sampling rate AFTER reading (prevents data loss)
                        if SAMPLING_INTERVAL > 0:
                            time.sleep(SAMPLING_INTERVAL)
                        
                    except UnicodeDecodeError:
                        error_count += 1
                        print("⚠️  Unicode decode error - skipping reading")
                        continue
                    except Exception as e:
                        error_count += 1
                        print(f"⚠️  Error reading data: {e}")
                        continue
                else:
                    # Small delay when no data available to avoid CPU spinning
                    time.sleep(0.001)
    
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print(" DATA COLLECTION STOPPED")
        print("="*70)
        print(f"📊 Total readings: {reading_count}")
        print(f"⚠️  Errors/skipped: {error_count}")
        print(f"⏱️  Duration: {elapsed/60:.1f} minutes")
        print(f"📈 Average rate: {reading_count/elapsed:.2f} readings/sec")
        print(f"💾 Data saved to: {filename}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        
    finally:
        ser.close()
        print("\n✓ Serial port closed")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    collect_data()


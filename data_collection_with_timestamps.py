"""
Enhanced Motor Data Collection Script with Timestamps
======================================================
Collects sensor data from Arduino and saves with timestamps
"""

import serial
import time
import datetime
import os
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================
SERIAL_PORT = 'COM3'  # Change to your Arduino port (use 'ls /dev/tty.*' on Mac/Linux)
BAUD_RATE = 115200
SAMPLING_INTERVAL = 1.0  # seconds between readings (0 for as fast as possible)

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
    print("\nPress Ctrl+C to stop collection\n")
    
    # Initialize serial connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✓ Serial connection established\n")
    except Exception as e:
        print(f"❌ Error connecting to serial port: {e}")
        print(f"   Make sure Arduino is connected to {SERIAL_PORT}")
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
            file.write("timestamp,ax_g,ay_g,az_g,mic_raw,temp_C\n")
            
            reading_count = 0
            error_count = 0
            start_time = time.time()
            
            print("📊 Collecting data...\n")
            
            while True:
                if ser.in_waiting > 0:
                    try:
                        # Capture timestamp immediately when data arrives
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        
                        # Read data from Arduino
                        data = ser.readline().decode('utf-8').strip()
                        
                        # Validate data
                        if not data or ',' not in data:
                            error_count += 1
                            continue
                        
                        # Check if data has correct number of columns (5 values expected)
                        data_parts = data.split(',')
                        if len(data_parts) != 5:
                            print(f"⚠️  Malformed data (expected 5 values, got {len(data_parts)}): {data}")
                            error_count += 1
                            continue
                        
                        # Write timestamped data
                        full_data = f"{timestamp},{data}"
                        file.write(full_data + '\n')
                        file.flush()  # Force write to disk
                        
                        reading_count += 1
                        
                        # Print progress every 10 readings
                        if reading_count % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = reading_count / elapsed if elapsed > 0 else 0
                            print(f"✓ Reading #{reading_count:4d} | Rate: {rate:.1f} Hz | Latest: {data}")
                        
                    except UnicodeDecodeError:
                        error_count += 1
                        print("⚠️  Unicode decode error - skipping reading")
                        continue
                    except Exception as e:
                        error_count += 1
                        print(f"⚠️  Error reading data: {e}")
                        continue
                
                # Optional: Control sampling rate
                if SAMPLING_INTERVAL > 0:
                    time.sleep(SAMPLING_INTERVAL)
    
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


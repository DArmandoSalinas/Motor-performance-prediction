// ==========================================================
// Motor Predictive Maintenance - Sensor Data Collection
// Compatible with data_collection_with_timestamps.py
// ==========================================================

// 1. LIBRERÍAS
// ==========================================================
#include <SPI.h>              
#include <PL_ADXL355.h>       
#include <Wire.h>             
#include <Adafruit_MLX90614.h> 

// ==========================================================
// 2. CONFIGURACIÓN DE PINES
// ==========================================================
// ADXL355 (SPI)
#define ADXL_CS_PIN 5 

// ==========================================================
// 3. OBJETOS Y VARIABLES
// ==========================================================
PL::ADXL355 adxl355; 
auto adxl_range = PL::ADXL355_Range::range2g;

Adafruit_MLX90614 mlx = Adafruit_MLX90614(); 

// ==========================================================
// 4. CONFIGURACIÓN
// ==========================================================
#define BAUD_RATE 460800      // Match Python script baud rate
#define SAMPLING_DELAY 2      // 2ms = 500 Hz (match Python: 0.002s)

void setup() {
  // Initialize serial at high baud rate for 500 Hz sampling
  Serial.begin(BAUD_RATE);
  while(!Serial); 
  
  // Initialize SPI for ADXL355
  SPI.begin(18, 19, 23, ADXL_CS_PIN); 
  adxl355.beginSPI(ADXL_CS_PIN);
  adxl355.setRange(adxl_range);
  adxl355.enableMeasurement();

  // Initialize MLX90614 temperature sensor
  mlx.begin();
  
  // Wait a moment for sensors to stabilize
  delay(100);
  
  // Print header (Python script will add timestamp)
  // Format: ax_g,ay_g,az_g,temp_C (4 values, no microphone)
  Serial.println("ax_g,ay_g,az_g,temp_C");
}

void loop() {
  // ==========================================
  // LECTURA 1: ADXL355 (Acelerómetro)
  // ==========================================
  auto accelerations = adxl355.getAccelerations();
  Serial.print(accelerations.x, 3); 
  Serial.print(",");
  Serial.print(accelerations.y, 3);
  Serial.print(",");
  Serial.print(accelerations.z, 3);
  
  // ==========================================
  // LECTURA 2: MLX90614 (Temperatura IR)
  // ==========================================
  float tempObjeto = mlx.readObjectTempC();    
  Serial.print(",");
  Serial.print(tempObjeto, 2);
  
  // End of line (Python will add timestamp)
  Serial.println();
  
  // Sampling delay: 2ms = 500 Hz
  delay(SAMPLING_DELAY);
}


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

void setup() {
  Serial.begin(115200);
  while(!Serial); 
  
  // --- Inicialización de sensores ---
  SPI.begin(18, 19, 23, ADXL_CS_PIN); 
  adxl355.beginSPI(ADXL_CS_PIN);
  adxl355.setRange(adxl_range);
  adxl355.enableMeasurement();

  mlx.begin();

  // Imprime la cabecera (una sola vez)
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
  Serial.println();
  
  delay(100); 
}


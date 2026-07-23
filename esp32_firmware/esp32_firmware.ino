// VL53L8CX -> STM32 Nucleo -> Serial streamer
// Streams one CSV line per frame: 64 comma-separated distance values (mm), 8x8 grid, row-major.
//
// Wiring (I2C, Nucleo-64 Arduino-shield header): VCC->3V3, GND->GND, SDA->D14, SCL->D15
//
// Board setup: Arduino IDE + STM32duino core (Tools > Board > STM32 boards > Nucleo-64,
// then pick your exact part number from the board's silkscreen). Upload method:
// STM32CubeProgrammer (SWD), uses the onboard ST-LINK.
//
// Library note: written against the SparkFun VL53L5CX Arduino library API, which is
// software-compatible with the L8CX in almost all forks/ports (same ULD driver lineage).
// If this doesn't compile against your installed library, search "VL53L8CX Arduino library"
// and swap the #include / class name below to match — the begin()/setResolution()/
// startRanging()/isDataReady()/getRangingData() calls should stay the same either way.
// This library has not been tested against STM32duino specifically -- if Wire calls inside
// it use any ESP32-only functions it may need small edits, but most Arduino I2C libraries
// stick to the standard Wire API and just work.

#include <Wire.h>
#include <SparkFun_VL53L5CX_Library.h>

SparkFun_VL53L5CX myImager;
VL53L5CX_ResultsData measurementData;

int imageResolution = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin();
  Wire.setClock(100000); // 100kHz Standard Mode -- deliberately slow. This board's onboard
                          // level shifter is known to be sensitive to wire length/capacitance;
                          // a slower clock tolerates that much better than 400kHz did. Bump
                          // this back up later once things are working reliably.

  Serial.println("Initializing VL53L8CX...");
  if (!myImager.begin()) {
    Serial.println("ERROR: sensor not found. Check wiring (SDA/SCL/VCC/GND). Halting.");
    while (1) { delay(1000); }
  }

  myImager.setResolution(8 * 8); // 64-zone (8x8) mode -- this is the whole point
  imageResolution = myImager.getResolution();

  myImager.setRangingFrequency(15); // Hz -- keep modest, stable I2C reads matter more than speed here
  myImager.startRanging();

  Serial.println("READY"); // Python script waits for this line before parsing frames
}

void loop() {
  if (myImager.isDataReady()) {
    if (myImager.getRangingData(&measurementData)) {
      for (int i = 0; i < imageResolution; i++) {
        Serial.print(measurementData.distance_mm[i]);
        if (i < imageResolution - 1) Serial.print(",");
      }
      Serial.println();
    }
  }
  delay(5);
}

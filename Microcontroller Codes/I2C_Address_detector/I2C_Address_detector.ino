#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial); // Wait for serial monitor to open
  Serial.println("Starting I2C device scan...");
}

void loop() {
  byte error, address;
  int nDevices = 0;

  Serial.println("\nScanning...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16)
        Serial.print("0");
      Serial.print(address, HEX);
      Serial.println("  ✔");
      nDevices++;
    } else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16)
        Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  if (nDevices == 0) {
    Serial.println("❌ No I2C devices found. Please check connections.");
  } else {
    Serial.print("✅ Scan complete. Devices found: ");
    Serial.println(nDevices);
  }

  delay(5000); // Wait 5 seconds before scanning again
}

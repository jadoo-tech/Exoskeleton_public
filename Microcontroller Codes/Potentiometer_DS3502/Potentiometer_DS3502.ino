#include <Adafruit_DS3502.h>

// PIN DEFINITIONS //
#define WIPER_VALUE_PIN A0
#define WIPER_MAX_PIN A1

// VARIABLE DEFINITIONS //
#define REF_V 5.0     // 5V by DEFAULT for arduino nano. use analogReference(EXTERNAL), and connect a stable reference voltage to the AREF pin
#define DIGITAL_MAX 1023
#define DELAY_TIME 1000
#define SETTLE_DELAY_TIME 10
#define RW_VAL_INCREASE_FACTOR 5
int RW_position = 0;

Adafruit_DS3502 ds3502;   // Note: can set RW position from 0 to 127.

void setup() {
  Serial.begin(115200);   // Set baud rate to 115200
  // analogReference(EXTERNAL)
  while (!Serial) { delay(1); }
  Serial.println("Adafruit DS3502 Test");

  // Initialize the DS3502 chip with the I2C address (0x29)
  if (!ds3502.begin(0x29)) {  
    Serial.println("DS3502 chip NOT found");
    while (1);
  }
  Serial.println("DS3502 chip found");
  Serial.println();
}

void loop() {
  float wiper_value;
  float max_voltage_value;
  
  ds3502.setWiper(RW_position);
  delay(SETTLE_DELAY_TIME);
  wiper_value = analogRead(WIPER_VALUE_PIN);      // Returns a digital value between 0 and 1023,
  max_voltage_value = analogRead(WIPER_MAX_PIN);  //  corresponding to the voltage between 0V and the reference voltage
  Serial.print("Analog Max Value read:  ");
  Serial.println(max_voltage_value);
  Serial.print("Analog Value read:      ");
  Serial.println(wiper_value);
  wiper_value *= REF_V / DIGITAL_MAX;
  Serial.print("Wiper voltage with wiper set to 0: ");
  Serial.print(wiper_value);
  Serial.println(" V");
  Serial.println();
  delay(DELAY_TIME);

  RW_position += RW_VAL_INCREASE_FACTOR;
  if (RW_position > 127){
    RW_position = 0;
  }
}

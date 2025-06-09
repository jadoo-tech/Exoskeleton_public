
// ========== Pin Setup ========== //
const int analogPins[] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9};
const int csPins[] = {12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2};
const int sckPin = 13;
#define SERIAL_PI Serial8 // Serial8 RX: 34 (not used for sending), TX: 35 (used to send)

const int numDev = sizeof(csPins)/sizeof(csPins[0]);
// ================================ //

// ========== Constants ========== //
// enables
bool RaspOutEn = false;
bool CSVEn = true;

// Timing
const unsigned long sampleIntervalMs = 1000;  // Sample every 1 second
unsigned long lastSampleTime = 0;
// ================================ //

void setup() {
  // Initialize chip select pins as outputs and set them LOW (activated)
  for (int i = 0; i < numDev; i++) {
    pinMode(csPins[i], OUTPUT);
    digitalWrite(csPins[i], LOW);  // Active = LOW
  }

  // Set SCK pin as output and set LOW initially
  pinMode(sckPin, OUTPUT);
  digitalWrite(sckPin, LOW);

  // Initialize Serial for laptop communication at 115200 baud
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial USB to be connected
  }
  Serial.println("Teensy 4.1 initialized.");

  // Initialize Serial8 for Raspberry Pi communication at 115200 baud
  SERIAL_PI.begin(115200);

  // Initialize analog pins (Arduino handles that automatically)

  // Optionally print header for CSV to laptop
  if (CSVEn) {
    Serial.print("Timestamp(ms)");
    for (int i = 0; i < numDev; i++) {
      Serial.print(",A");
      Serial.print(i);
    }
    Serial.println();
  }
}

void loop() {
  // Check for commands on Serial to toggle sending
  handleCommands();

  unsigned long now = millis();
  if (now - lastSampleTime >= sampleIntervalMs) {
    lastSampleTime = now;

    // Read analog voltages
    int analogValues[numDev];
    for (int i = 0; i < numDev; i++) {
      analogValues[i] = analogRead(analogPins[i]);
    }

    // Pulse SCK pin (simulate clock)
    digitalWrite(sckPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(sckPin, LOW);

    // Send data to Raspberry Pi via Serial8 if enabled
    if (RaspOutEn) {
      // Format data as CSV line: timestamp, val0, val1, ...
      SERIAL_PI.print(now);
      for (int i = 0; i < numDev; i++) {
        SERIAL_PI.print(",");
        SERIAL_PI.print(analogValues[i]);
      }
      SERIAL_PI.println();
    }

    // Send CSV data to laptop over USB serial if enabled
    if (CSVEn) {
      Serial.print(now);
      for (int i = 0; i < numDev; i++) {
        Serial.print(",");
        Serial.print(analogValues[i]);
      }
      Serial.println();
    }
  }
}

// Function to parse commands from Serial (laptop) to toggle features
void handleCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("pi_on")) {
      RaspOutEn = true;
      Serial.println("Sending to Raspberry Pi enabled.");
    } else if (cmd.equalsIgnoreCase("pi_off")) {
      RaspOutEn = false;
      Serial.println("Sending to Raspberry Pi disabled.");
    } else if (cmd.equalsIgnoreCase("csv_on")) {
      CSVEn = true;
      Serial.println("CSV output to laptop enabled.");
      // Print CSV header when enabling
      Serial.print("Timestamp(ms)");
      for (int i = 0; i < numDev; i++) {
        Serial.print(",A");
        Serial.print(i);
      }
      Serial.println();
    } else if (cmd.equalsIgnoreCase("csv_off")) {
      CSVEn = false;
      Serial.println("CSV output to laptop disabled.");
    } else {
      Serial.println("Unknown command. Use: pi_on, pi_off, csv_on, csv_off");
    }
  }
}

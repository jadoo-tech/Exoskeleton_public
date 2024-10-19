#include <Arduino.h>

// Constants
const int analogPins[] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17};  
const int numPins = 18;  // Total number of analog pins
int sampleRate = 1000;  // Default sample rate

// Buffers for storing the data
float buffer[numPins];  // Store readings as voltage values
bool activePins[numPins];  // Active pins to read

// Timer interrupt to read analog values
IntervalTimer sampleTimer;
uint16_t counter=0;
// Function to convert raw ADC values to voltage
float adcToVoltage(int rawValue) {
    return (rawValue / 4095.0) * 3.3;  // Scale based on reference voltage
}

void sampleData() {
    for (int i = 0; i < numPins; i++) {
        if (activePins[i]) {  // Only read from active pins
            int rawValue = analogRead(analogPins[i]);  // Read the raw ADC value
            buffer[i] = adcToVoltage(rawValue);  // Convert to voltage and store
            //buffer[i] = counter;
        }
    }

    // Send the active pin data over USB serial
    Serial.write((uint8_t*)buffer, sizeof(buffer));  // Send the voltage values as raw bytes
    counter+=1;
    // Add a manual delay to throttle the sample rate further
    delayMicroseconds(500);  // Adjust this delay to achieve the desired sample rate
}

void setup() {
    // Start serial communication at 115200 baud
    Serial.begin(115200);
    while (!Serial) { /* Wait for serial port to be available */ }

    // Initialize the analog pins and set all as inactive by default
    for (int i = 0; i < numPins; i++) {
        pinMode(analogPins[i], INPUT);
        activePins[i] = false;  // Initially mark all pins as inactive
    }

    // Wait for the serial command to specify which pins to activate and the sample rate
    while (!Serial.available()) { /* Wait for command */ }

    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        // Example command: "SET SR 1000;RT 5;AP 0,5"
        if (command.startsWith("SET SR")) {
            int srIndex = command.indexOf("SR ") + 3;
            int rtIndex = command.indexOf(";RT");
            sampleRate = command.substring(srIndex, rtIndex).toInt();  // Extract sample rate

            // Extract pins after "AP" command
            String pinList = command.substring(command.indexOf("AP ") + 3);
            while (pinList.length() > 0) {
                int nextIndex = pinList.indexOf(',');
                String pinStr = pinList.substring(0, nextIndex == -1 ? pinList.length() : nextIndex);
                int pinIndex = pinStr.toInt();
                if (pinIndex >= 0 && pinIndex < numPins) {
                    activePins[pinIndex] = true;  // Activate this pin
                }
                if (nextIndex == -1) break;
                pinList = pinList.substring(nextIndex + 1);
            }
        }
    }

    // Set up the timer to sample data at the specified sample rate
    sampleTimer.begin(sampleData, 1000000 / sampleRate);  // Timer interval in microseconds
}

void loop() {
    // The loop is empty because the sampling is handled by the timer interrupt
}
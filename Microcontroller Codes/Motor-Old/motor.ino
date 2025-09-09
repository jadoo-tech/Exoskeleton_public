//Part of the serial interpreter portion of this code is from https://gist.github.com/edgar-bonet/607b387260388be77e96
#include <Arduino.h>
#include <avr/pgmspace.h>
#include <Stepper.h>
// #define USBSERIAL Serial
#define BUF_LENGTH 128  /* Buffer for the incoming command. */


#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11

#define SPEED 60  //speed at rpm

// Number of steps per output rotation
const int stepsPerRevolution = 200;

// Create Instance of Stepper library
Stepper stepper = Stepper(stepsPerRevolution, IN1, IN2, IN3, IN4);
static bool do_echo = false;

static void exec(char *cmdline)
{
    char *command = strsep(&cmdline, " ");

    if (strcmp_P(command, PSTR("help")) == 0) {
        Serial.println(F(
            "mode <pin> <mode>: pinMode()\r\n"
            "step <steps>: step()\r\n"));
    } else if (strcmp_P(command, PSTR("mode")) == 0) {
        int pin = atoi(strsep(&cmdline, " "));
        int mode = atoi(cmdline);
        pinMode(pin, mode);
    } else if (strcmp_P(command, PSTR("step")) == 0) {
        int steps = atoi(strsep(&cmdline, " "));
        stepper.step(steps);
    } else {
        Serial.print(F("Error: Unknown command: "));
        Serial.println(command);
    }
}
void setup() {
  Serial.begin(9600);
  stepper.setSpeed(SPEED);
  
  delay(2);
}

void loop() {
  while (Serial.available()) {
        static char buffer[BUF_LENGTH];
        static int length = 0;

        int data = Serial.read();
        if (data == '\b' || data == '\177') {  // BS and DEL
            if (length) {
                length--;
            }
        }
        else if (data == '\r') {
            if (do_echo) Serial.write("\r\n");    // output CRLF
            buffer[length] = '\0';
            if (length) exec(buffer);
            length = 0;
        }
        else if (length < BUF_LENGTH - 1) {
            buffer[length++] = data;
            if (do_echo) Serial.write(data);
        }
    }
}

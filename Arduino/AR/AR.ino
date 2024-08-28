#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
#define COLOR_MODE {SSD1306_BLACK, SSD1306_WHITE}  // COLOR_MODE[0] = Off, COLOR_MODE[1] = On
String outputStrings[] = {"cat", "orv", "Waqas"};
int stringNums = 3; // len(outputStrings)

// Declaration for SSD1306 display connected using SPI (hardware SPI)
#define OLED1_MOSI 3
#define OLED1_CLK 2
#define OLED1_DC 15
#define OLED1_CS 13
#define OLED1_RESET 14
Adafruit_SSD1306 display1(SCREEN_WIDTH, SCREEN_HEIGHT, OLED1_MOSI, OLED1_CLK, OLED1_DC, OLED1_RESET, OLED1_CS);

#define OLED2_MOSI 3
#define OLED2_CLK 2
#define OLED2_DC 7
#define OLED2_CS 5
#define OLED2_RESET 6
Adafruit_SSD1306 display2(SCREEN_WIDTH, SCREEN_HEIGHT, OLED2_MOSI, OLED2_CLK, OLED2_DC, OLED2_RESET, OLED2_CS);

// #define USBSERIAL Serial
#define BUF_LENGTH 128  /* Buffer for the incoming command. */
static bool do_echo = false;

void setup() {
  Serial.begin(9600);

  if (!display1.begin(SSD1306_SWITCHCAPVCC, OLED1_CS)) {
    Serial.println(F("SSD1306 allocation failed (1)"));
    for (;;)
      ;
  }

  if (!display2.begin(SSD1306_SWITCHCAPVCC, OLED2_CS)) {
    Serial.println(F("SSD1306 allocation failed (2)"));
    for (;;)
      ;
  }

  display1.setRotation(3);
  display2.setRotation(3);

  display1.display();
  display2.display();
  delay(2000);

  display1.clearDisplay();
  display2.clearDisplay();

  display1.setTextSize(1);
  display1.setTextColor(SSD1306_WHITE);
  display1.setCursor(0, 3);
  display1.print("Look");
  display1.setTextSize(1);
  display1.setTextColor(SSD1306_WHITE);
  display1.setCursor(0, 15);
  display1.print("Left");

  display2.setTextSize(1);
  display2.setTextColor(SSD1306_WHITE);
  display2.setCursor(0, 3);
  display2.print("Look");
  display2.setTextSize(1);
  display2.setTextColor(SSD1306_WHITE);
  display2.setCursor(0, 15);
  display2.print("Left");

  blinkDisplay(true);

  display1.display();
  display2.display();
}

void loop() {
  static unsigned long lastFlash = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastFlash >= 500) {
    lastFlash = currentMillis;
    static bool arrowVisible = true;
    arrowVisible = !arrowVisible;

    blinkDisplay(arrowVisible);
  }

  if (Serial.available()){
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

void blinkDisplay(bool visible) {
  uint16_t color = visible ? SSD1306_WHITE : SSD1306_BLACK;

  for (int i = 0; i < stringNums; i++) {
    display1.setTextSize(1);
    display1.setTextColor(color);
    display1.setCursor(0, 77 + (i * 10));
    display1.print(outputStrings[i]);

    display2.setTextSize(1);
    display2.setTextColor(color);
    display2.setCursor(0, 77 + (i * 10));
    display2.print(outputStrings[i]);
  }

  display1.drawLine(5, 60, 15, 50, color);
  display1.drawLine(5, 60, 15, 70, color);
  display1.drawLine(15, 50, 15, 70, color);
  display1.display();

  display2.drawLine(5, 60, 15, 50, color);
  display2.drawLine(5, 60, 15, 70, color);
  display2.drawLine(15, 50, 15, 70, color);
  display2.display();
}

static void exec(char *cmdline) {
  char *command = strsep(&cmdline, " ");

  if (strcmp_P(command, PSTR("help")) == 0) {
    Serial.print("display <index between 0 ~ ");
    Serial.print(stringNums-1);
    Serial.println(F(
      "> <word to display>: display()\r\n"
      ""));
  } else if (strcmp_P(command, PSTR("display")) == 0) {
    int ind = atoi(strsep(&cmdline, " "));
      if ((ind < 0) || (ind >= stringNums)){
        ind = 0;
      }
      String word = cmdline;
      outputStrings[ind] = word;
  } else {
    Serial.print(F("Error: Unknown command: "));
    Serial.println(command);
  }
}

# Debug Steps:
1. Make sure all the libraries are installed
2. If you get an error , go to Arduino's library folder and find "Adafruit_SSD1306.cpp" in folder the library folder (it defaults to ~/Document/Arduino/libraries/Adafruit_SSD1306). Comment the line "#include <pgmspace.h>" out
3. For noisy screen, check the pins. If they are correct, make sure the connection is secure.
4. If nothing works, re-write the code without copy and pasting..

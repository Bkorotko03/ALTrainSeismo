// required sd card libraries
#include <SPI.h>
#include <SD.h>

int sensorValue = 0; // initialize sensor value as 0
const int chipSelect = 10; // pick chip select pin to be 10, this is the case for dedicated spi headers
File myFile; // initialize file
const int ledPin = LED_BUILTIN; // set up LED pin

void setup() {
  // this stuff runs only once
  Serial.begin(9600); // initialize serial

while (!Serial);

  Serial.print("Initializing SD card...");

  if (!SD.begin(chipSelect)) {
    Serial.println("initialization failed."); // if cant select chip, cry
      while (1) {
        digitalWrite(ledPin, HIGH);
        delay(100);
        digitalWrite(ledPin, LOW);
        delay(100);
      }; // hold in loop, dont run rest of code
  }
  Serial.println("initialization done.");

  if (SD.exists("example.txt")) {
    Serial.println("example.txt exists.");
  } else {
    Serial.println("example.txt doesn't exist.");
  }

  Serial.println("Creating example.txt...");

}

void loop() {
  // put your main code here, to run repeatedly:
  sensorValue = analogRead(A0);

  Serial.println(sensorValue);

  myFile = SD.open("example.txt", FILE_WRITE);

  if (myFile) {
    myFile.println(sensorValue);
    myFile.println("buffer statement lol :3");
  }

  myFile.close();

  delay(100);
}

#include <SPI.h>
#include <SD.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

#define GPSECHO false // echos the GPS data to the serial output
#define BUFFER_SIZE 512 // buffer for writes to SD card

int sensorValue = 0; // initialize sensor value as 0
const int chipSelect = 10; // pick chip select pin to be 10, this is the case for dedicated spi headers
File myFile; // initialize file
const int ledPin = LED_BUILTIN; // set up LED pin
char buffer[BUFFER_SIZE];
int bufferIndex = 0;
uint32_t lastLogTime = 0;
const uint16_t LOG_INTERVAL_MS = 100;

uint32_t gpsSyncMillis = 0;
uint8_t gpsSyncHour = 0;
uint8_t gpsSyncMinute = 0;
uint8_t gpsSyncSecond = 0;

int lastGPSSec = -1;

bool fileInitialized = false;
char filename[32];

// initialize serial for GPS
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

void setup() {
  // this stuff runs only once
  Serial.begin(115200); // initialize serial 115200 baud
  delay(5000);
  Serial.println("Initializing Adafruit GPS Shield");

  GPS.begin(9600); // initialize link to GPS module at 9600 baud
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // request minimum recommended data and fix data (altitude and things)
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // request updates at 1 Hz, this should be the quickest we get these guys
  GPS.sendCommand(PGCMD_ANTENNA); // get updates on antenna status

  delay(1000);

  Serial.println("GPS initialized?");

// while (!Serial);

  Serial.println("Initializing SD card...");

  if (!SD.begin(chipSelect)) {
    Serial.println("initialization failed."); // if cant select chip, cry
      while (1) {
        Serial.println("SD Card Broken!!! :(");
        digitalWrite(ledPin, HIGH);
        delay(100);
        digitalWrite(ledPin, LOW);
        delay(100);
      }; // hold in loop, dont run rest of code
  }
  Serial.println("SD card initialization done.");

  // myFile = SD.open("datalog.csv", FILE_WRITE);

  // if (!myFile) {
  //   Serial.println("File open failed!");
  //   while (1);
  // }

  // if (myFile.size() == 0) {
  //   myFile.println("timecode,lat,lat_dir,lon,lon_dir,sensor");
  //   myFile.flush();
  // }

  Serial.println("Logger ready.");

  // if (SD.exists("datalog.csv")) {
  //   Serial.println("example.txt exists.");
  // } else {
  //   Serial.println("example.txt doesn't exist.");
  // }

  // Serial.println("Creating example.txt...");

  // String filename = "datalog_" + GPS.hour;

  // Serial.println(filename);

}

// uint32_t timer = millis();
void loop() {
  char c = GPS.read();
  if ((c) && (GPSECHO)) // if there is GPS data and we want echo, print data to serial
    Serial.write(c);

  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

// time to parse the GPS data
  if (millis() - lastLogTime >= LOG_INTERVAL_MS) {
    lastLogTime = millis(); // reset the timer
    // Serial.println("Timer reset");

    if (GPS.fix) {

      if (GPS.seconds != lastGPSSec) {
        lastGPSSec = GPS.seconds;

        gpsSyncMillis = millis();
        gpsSyncHour = GPS.hour;
        gpsSyncMinute = GPS.minute;
        gpsSyncSecond = GPS.seconds;
      }

      uint32_t elapsed = millis() - gpsSyncMillis;

      uint32_t totalSeconds = gpsSyncHour * 3600UL + gpsSyncMinute * 60UL + gpsSyncSecond + (elapsed / 1000);

      uint16_t ms = elapsed % 1000;

      uint8_t hour = (totalSeconds / 3600) % 24;
      uint8_t minute = (totalSeconds / 60) % 60;
      uint8_t second = totalSeconds % 60;

      int sensorValue = analogRead(A0);
      Serial.println("GPS fixed");

      if (!fileInitialized && 2020 < GPS.year < 2050) { // assuming no one uses this past 2050 lmao
        snprintf(filename,sizeof(filename),
        "%02d%02d%02d%02d.csv",
        GPS.year,GPS.month,GPS.day,GPS.seconds);
        
        Serial.print("Creating file: ");
        Serial.println(filename);

        myFile = SD.open(filename, FILE_WRITE);

        if (!myFile) {
          Serial.println("File creating failed.");
          return;
        }

        myFile.println("timecode,lat,lat_dir,lon,lon_dir,sensor");
        myFile.flush();

        fileInitialized = true;

        Serial.println("File initialized.");
      }

      // ensure we don't overflow buffer
      if (bufferIndex < BUFFER_SIZE - 120) {
        int len = snprintf(&buffer[bufferIndex],
                   BUFFER_SIZE - bufferIndex,
                   "%02d%02d%02d_%02d%02d%02d_%03d,%.4f,%c,%.4f,%c,%d\n",
                   GPS.year, GPS.month, GPS.day,
                   hour, minute, second, ms,
                   GPS.latitude, GPS.lat,
                   GPS.longitude, GPS.lon,
                   sensorValue);
        
        // Serial.println("Wrote to buffer");

        if (len > 0) bufferIndex += len;
    }
  }

  if (bufferIndex >= BUFFER_SIZE - 120) {
    myFile.write((uint8_t*)buffer, bufferIndex);
    myFile.flush();   // ensures data is committed
    bufferIndex = 0;
    Serial.println("Buffer pushed to SD card");
  }
  }
  // delay(100);
}

// data recording program for each of the arduinos
// takes analog reading at *10 Hz* and syncs with the GPS satellite at *1 Hz*
// hopefully there are good comments

// imports
#include <SPI.h>
#include <SD.h> // want to switch to better SD library for full timecode filenames
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <Arduino_Modulino.h>

#define GPSECHO false // echos the GPS data to the serial output
#define BUFFER_SIZE 512 // size of buffer for writes to SD card

ModulinoBuzzer buzzer; // initialize the buzzer object
int soundf = 440; // sound frequency
int soundd = 200; // sound duration

int sensorValue = 0; // initialize sensor value as 0
const int chipSelect = 10; // pick chip select pin to be 10, this is the case for dedicated spi headers
const int ledPin = LED_BUILTIN; // set up LED pin

File myFile; // initialize file variable
char filename[32]; // empty var for filename
bool fileInitialized = false; // do we have a file to write to?

char buffer[BUFFER_SIZE]; // initialize write buffer
int bufferIndex = 0; // how filled is our write buffer
uint32_t lastLogTime = 0; // when did we last log data
const uint16_t LOG_INTERVAL_MS = 100; // how often we measure signal, could need to be much quicker

// global variables for > 1 Hz recording frequency
uint32_t gpsSyncMillis = 0;
uint8_t gpsSyncHour = 0;
uint8_t gpsSyncMinute = 0;
uint8_t gpsSyncSecond = 0;

int lastGPSSec = -1; // for sync mentioned above

bool gpsfixbool = false; // initial gps fix test

// initialize serial for GPS
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

void setup() { // this stuff runs only once
// ------------------------------------ Buzzer -----------------------
  // Some notes on the audio error codes:
  // One beep is good, continuous beeps are really mf bad
  Modulino.begin();
  buzzer.begin();

// ------------------------------------------- GPS and Serial --------------------------------------------------------
  Serial.begin(115200); // initialize serial 115200 baud
  delay(2000);
  Serial.println("Initializing Adafruit GPS Shield");
  buzzer.tone(soundf,soundd);
  delay(2*soundd);

  GPS.begin(9600); // initialize link to GPS module at 9600 baud
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // request minimum recommended data and fix data (altitude and things)
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // request updates at 1 Hz, this should be the quickest we get these guys
  GPS.sendCommand(PGCMD_ANTENNA); // get updates on antenna status

  delay(1000);

  Serial.println("GPS initialized?"); // there should be some conditional here to check if this is right
  buzzer.tone(soundf,soundd);
  delay(soundd);
  delay(1000);

// ------------------------------------------- SD Card----------------------
  Serial.println("Initializing SD card...");
  buzzer.tone(soundf,soundd);
  delay(soundd);
  delay(1000);

  if (!SD.begin(chipSelect)) {
    Serial.println(" SD card initialization failed."); // if cant select chip, cry
      while (1) {
        Serial.println("SD Card Broken!!! :(");
        digitalWrite(ledPin, HIGH);
        buzzer.tone(soundf,soundd);
        delay(2*soundd);
        digitalWrite(ledPin, LOW);
        buzzer.tone(soundf,soundd);
        delay(2*soundd);
      }; // hold in loop, dont run rest of code
  }
  Serial.println("SD card initialized.");
  Serial.println("Waiting for GPS fix...");
  buzzer.tone(soundf,soundd);
  delay(2*soundd);

}

void loop() { // this thing runs constantly from startup until power loss, want to be able to shutdown gracefully
  char c = GPS.read();
  if ((c) && (GPSECHO)) // if there is GPS data and we want echo, print data to serial
    Serial.write(c);

  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false *this comment is from the example sketch in the package*
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

// time to parse the GPS data
  if (millis() - lastLogTime >= LOG_INTERVAL_MS) { // if its been at least a log interval, do below
    lastLogTime = millis(); // reset the timer
    // Serial.println("Timer reset"); // debug

    if (GPS.fix) { // we wait until we get a gps lock to do any kind of recording or naming

      Serial.println("GPS fixed"); // what a surprise

      if (gpsfixbool = false) {
        buzzer.tone(soundf,soundd);
        delay(soundd);
      }

      // begin time sync for the more frequent measurements
      if (GPS.seconds != lastGPSSec) {
        lastGPSSec = GPS.seconds;

        gpsSyncMillis = millis();
        gpsSyncHour = GPS.hour;
        gpsSyncMinute = GPS.minute;
        gpsSyncSecond = GPS.seconds;
      }

      // local variables for syncing
      uint32_t elapsed = millis() - gpsSyncMillis;

      uint32_t totalSeconds = gpsSyncHour * 3600UL + gpsSyncMinute * 60UL + gpsSyncSecond + (elapsed / 1000); // convert GPS time into total seconds
      float elapsedSeconds = gpsSyncHour * 3600.0f + gpsSyncMinute * 60.0f + gpsSyncSecond + (elapsed / 1000.0f); // want this to output in csv as a float

      // now convert new time back to hh mm ss msmsms
      uint16_t ms = elapsed % 1000;
      uint8_t hour = (totalSeconds / 3600) % 24;
      uint8_t minute = (totalSeconds / 60) % 60;
      uint8_t second = totalSeconds % 60;

      int sensorValue = analogRead(A0); // read from pin A0 (still need to figure out how to convert them integers to a real voltage measurement)

      if (!fileInitialized && GPS.year >= 25 && GPS.year <= 27) { // check if file not initialized and sanity check that the GPS data makes sense
        snprintf(filename,sizeof(filename), // the filename based on timecode
        "%02d%02d%02d%02d.csv", // limited to 8 characters before extension because of bad SD card library
        GPS.year,GPS.month,GPS.day,GPS.hour);
        
        Serial.print("Creating file: ");
        Serial.println(filename);
        buzzer.tone(soundf,soundd);
        delay(soundd);

        myFile = SD.open(filename, FILE_WRITE); // open / create file for write

        if (!myFile) {
          Serial.println("File creating failed.");
          while(1) {
            buzzer.tone(soundf,soundd);
            delay(2*soundd);
          }
        }

        myFile.println("timecode,seconds,lat,lat_dir,lon,lon_dir,sensor"); // make CSV headers and push to the file
        myFile.flush();

        fileInitialized = true; // set bool

        Serial.println("File initialized.");
        buzzer.tone(soundf,soundd);
        delay(soundd);
      }

      if (bufferIndex < BUFFER_SIZE - 120) { // ensure we don't overflow buffer
        int len = snprintf(&buffer[bufferIndex], // print below things to buffer
                   BUFFER_SIZE - bufferIndex,
                   "%02d%02d%02d_%02d%02d%02d_%03d,%.3f,%.4f,%c,%.4f,%c,%d\n", // format of data to print
                   GPS.year, GPS.month, GPS.day, hour, minute, second, ms, elapsedSeconds, GPS.latitude, GPS.lat, GPS.longitude, GPS.lon, sensorValue); // values to write
        
        // Serial.println("Wrote to buffer"); // debug

        if (len > 0) bufferIndex += len;
    }
  }

  if (bufferIndex >= BUFFER_SIZE - 120) { // check if we're close to full
    myFile.write((uint8_t*)buffer, bufferIndex);
    myFile.flush();   // ensures data is committed
    bufferIndex = 0;
    Serial.println("Buffer pushed to SD card");
  }
  }
}

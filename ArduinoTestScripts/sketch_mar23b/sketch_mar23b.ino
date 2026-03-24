#include <SPI.h>
#include <SD.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

// ---------------- CONFIG ----------------
#define GPSECHO false
#define CHIP_SELECT 10
#define BUFFER_SIZE 512

// logging rate (ms)
const uint16_t LOG_INTERVAL_MS = 100;  // 10 Hz

// ---------------- GPS ----------------
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

// ---------------- SD + BUFFER ----------------
File myFile;

char buffer[BUFFER_SIZE];
int bufferIndex = 0;

// ---------------- TIMING ----------------
uint32_t lastLogTime = 0;

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("Starting logger...");

  // GPS setup
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_ANTENNA);

  // SD setup
  if (!SD.begin(CHIP_SELECT)) {
    Serial.println("SD init failed!");
    while (1);
  }

  myFile = SD.open("datalog.csv", FILE_WRITE);
  if (!myFile) {
    Serial.println("File open failed!");
    while (1);
  }

  // Only write header if file is empty
  if (myFile.size() == 0) {
    myFile.println("millis,time,lat,lat_dir,lon,lon_dir,sensor");
    myFile.flush();
  }

  Serial.println("Logger ready.");
}

// ---------------- LOOP ----------------
void loop() {
  // -------- ALWAYS SERVICE GPS --------
  char c = GPS.read();
  if ((c) && (GPSECHO)) Serial.write(c);

  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) return;
  }

  // Serial.println("New loop");

  // -------- LOGGING --------
  if (millis() - lastLogTime >= LOG_INTERVAL_MS) {
    lastLogTime = millis();
    // Serial.println("New log");

    if (GPS.fix) {
      int sensorValue = analogRead(A0);
      Serial.println("GPS fixed");

      // ensure we don't overflow buffer
      if (bufferIndex < BUFFER_SIZE - 100) {
        int len = snprintf(&buffer[bufferIndex],
                           BUFFER_SIZE - bufferIndex,
                           "%lu,%02d:%02d:%02d,%.4f,%c,%.4f,%c,%d\n",
                           millis(),
                           GPS.hour, GPS.minute, GPS.seconds,
                           GPS.latitude, GPS.lat,
                           GPS.longitude, GPS.lon,
                           sensorValue);
        
        // Serial.println("Wrote to buffer");

        if (len > 0) bufferIndex += len;
      }
    }
  }

  // -------- SAFE SD WRITE (BLOCK, NOT BYTE-BY-BYTE) --------
  if (bufferIndex >= BUFFER_SIZE - 100) {
    myFile.write((uint8_t*)buffer, bufferIndex);
    myFile.flush();   // ensures data is committed
    bufferIndex = 0;
    Serial.println("Buffer pushed to SD card");
  }
}
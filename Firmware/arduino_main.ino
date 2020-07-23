#include "TinyGPS.h"

TinyGPS gps;

#define GPS_TX_DIGITAL_OUT_PIN 5
#define GPS_RX_DIGITAL_OUT_PIN 6

long startMillis;
long secondsToFirstLocation = 0;

#define DEBUG

float latitude = 0.0;
float longitude = 0.0;

void setup()
{
  #ifdef DEBUG
  Serial.begin(19200);
  #endif
  
  // Serial1 is GPS
  Serial1.begin(9600);
  
  // prevent controller pins 5 and 6 from interfering with the comms from GPS
 // pinMode(GPS_TX_DIGITAL_OUT_PIN, INPUT);
 // pinMode(GPS_RX_DIGITAL_OUT_PIN, INPUT);
  
  startMillis = millis();
  Serial.println("Starting........");
}

void loop()
{
  readLocation();
}

//--------------------------------------------------------------------------------------------
void readLocation(){
  bool newData = false;
  unsigned long chars = 0;
  unsigned short sentences, failed;

  // For one second we parse GPS data and report some key values
  for (unsigned long start = millis(); millis() - start < 1000;)
  {
    while (Serial1.available())
    {
      int c = Serial1.read();
//      Serial.print((char)c); // if you uncomment this you will see the raw data from the GPS
      ++chars;
      if (gps.encode(c)) // Did a new valid sentence come in?
        newData = true;
    }
  }
  
  if (newData)
  {
    // we have a location fix so output the lat / long and time to acquire
    if(secondsToFirstLocation == 0){
      secondsToFirstLocation = (millis() - startMillis) / 1000;
      Serial.print("Acquired in:");
      Serial.print(secondsToFirstLocation);
      Serial.println("s");
    }
    
    unsigned long age;
    gps.f_get_position(&latitude, &longitude, &age);
    
    latitude == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : latitude;
    longitude == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : longitude;
    
    Serial.print("Location: ");
    Serial.print(latitude, 6);
    Serial.print(" , ");
    Serial.print(longitude, 6);
    Serial.println("");
  }
  
  if (chars == 0){
    // if you haven't got any chars then likely a wiring issue
    Serial.println("Check wiring");
  }
  else if(secondsToFirstLocation == 0){
    // still working
  }
}

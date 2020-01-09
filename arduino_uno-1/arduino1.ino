// Example testing sketch for various DHT humidity/temperature sensors
// Written by ladyada, public domain

// REQUIRES the following Arduino libraries:
// - DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library
// - Adafruit Unified Sensor Lib: https://github.com/adafruit/Adafruit_Sensor

#include "DHT.h"
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// Digital pin connected to the DHT sensor
#define DHTPIN 2

#define DHTTYPE DHT11

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

#define RX 5
#define TX 6

SoftwareSerial s(RX, TX);


void setup() {
  Serial.begin(9600);

  // To begin the serial communication between Arduino and NodeMCU with 9600 bits per second
  s.begin(9600);

  dht.begin();
}

void communicate() {
  const int capacity = JSON_OBJECT_SIZE(2);
  StaticJsonDocument<capacity> doc;

  doc["temperature"] = 20;
  doc["humidity"] = 80;

  // s.write(doc);
  serializeJson(doc, s);
}

void loop() {
  // delay(2000);

  // // Reading temperature or humidity takes about 250 milliseconds!
  // // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // float h = dht.readHumidity();
  // // Read temperature as Celsius (the default)
  // float t = dht.readTemperature();
  // // Read temperature as Fahrenheit (isFahrenheit = true)
  // float f = dht.readTemperature(true);

  // // Check if any reads failed and exit early (to try again).
  // if (isnan(h) || isnan(t) || isnan(f)) {
  //   Serial.println(F("Failed to read from DHT sensor!"));
  //   return;
  // }

  // // Compute heat index in Fahrenheit (the default)
  // float hif = dht.computeHeatIndex(f, h);
  // // Compute heat index in Celsius (isFahreheit = false)
  // float hic = dht.computeHeatIndex(t, h, false);

  // Serial.print(F("Humidity: "));
  // Serial.print(h);
  // Serial.print(F("%  Temperature: "));
  // Serial.print(t);
  // Serial.print(F("°C "));
  // Serial.print(f);
  // Serial.print(F("°F  Heat index: "));
  // Serial.print(hic);
  // Serial.print(F("°C "));
  // Serial.print(hif);
  // Serial.println(F("°F"));

  communicate();
}

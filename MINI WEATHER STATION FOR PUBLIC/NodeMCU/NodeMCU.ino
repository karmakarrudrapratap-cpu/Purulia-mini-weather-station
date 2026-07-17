/*
 * ESP8266 Sensor Node
 * Sends BMP280 + DHT11 data to ESP32-S3
 *
 * Connections
 * -----------------------
 * BMP280
 * D1(GPIO5)  -> SCL
 * D2(GPIO4)  -> SDA
 *
 * DHT11
 * D4(GPIO2)  -> DATA
 *
 * ESP32
 * ESP8266 TX(GPIO1) ----> ESP32 RX(GPIO44)
 * ESP8266 GND ----------> ESP32 GND
 */

#include <ESP8266WiFi.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_BMP280.h>

#define DHTPIN 2
#define DHTTYPE DHT11

#define BMP_SDA 4
#define BMP_SCL 5

DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP280 bmp;

unsigned long lastSend = 0;

const unsigned long SEND_INTERVAL = 5000;

void setup()
{
    Serial.begin(115200);

    delay(1000);

    Wire.begin(BMP_SDA, BMP_SCL);

    dht.begin();

    if (!bmp.begin(0x76))
    {
        bmp.begin(0x77);
    }

    Serial.println();
    Serial.println("ESP8266 Started");
}

void sendPacket(float t, float h, float p)
{
    Serial.print("SENSOR|");
    Serial.print(t, 2);
    Serial.print("|");
    Serial.print(h, 2);
    Serial.print("|");
    Serial.print(p, 2);
    Serial.print("|");
    Serial.print(millis());
    Serial.print("#");
}

void loop()
{
    if (millis() - lastSend >= SEND_INTERVAL)
    {
        lastSend = millis();

        float temp = bmp.readTemperature();
        float hum = dht.readHumidity();
        float press = bmp.readPressure() / 100.0;

        if (isnan(temp))
            temp = 0;

        if (isnan(hum))
            hum = 0;

        if (isnan(press))
            press = 0;

        // Debug (USB Serial Monitor)
        Serial.println();
        Serial.println("----------------------------");
        Serial.print("Temperature : ");
        Serial.println(temp);

        Serial.print("Humidity    : ");
        Serial.println(hum);

        Serial.print("Pressure    : ");
        Serial.println(press);

        Serial.println("----------------------------");

        // Send packet
        sendPacket(temp, hum, press);
    }
}
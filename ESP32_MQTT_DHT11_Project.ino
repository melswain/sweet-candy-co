/*********
https://www.electronicshub.org/esp32-dht11-tutorial/
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#define DHT11PIN 26
// #include <Wire.h>
// #include <Adafruit_BME280.h>
// #include <Adafruit_Sensor.h>
DHT dht(DHT11PIN, DHT11);

// Replace the next variables with your SSID/Password combination
// const char* ssid = "REPLACE_WITH_YOUR_SSID";
// const char* password = "REPLACE_WITH_YOUR_PASSWORD";
const char* ssid = "Yakin Iphone";
const char* password = "YakinSucces";

// Add your MQTT Broker IP address, example:
//const char* mqtt_server = "192.168.1.144";
//const char* mqtt_server = "YOUR_MQTT_BROKER_IP_ADDRESS";
const char* mqtt_server = "172.20.10.12";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

//uncomment the following lines if you're using SPI
/*#include <SPI.h>
#define BME_SCK 18
#define BME_MISO 19
#define BME_MOSI 23
#define BME_CS 5*/

//Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI
//float temperature = 0;
//float humidity = 0;

// LED Pin
const int ledPin = 4;

void setup() {
  Serial.begin(115200);
  dht.begin();
  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  //status = bme.begin();  
  // if (!bme.begin(0x76)) {
  //   Serial.println("Could not find a valid BME280 sensor, check wiring!");
  //   while (1);
  // }
  setup_wifi();
  client.setServer(mqtt_server, 1883);
 // client.setCallback(callback);

  pinMode(ledPin, OUTPUT);
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// void callback(char* topic, byte* message, unsigned int length) {
//   Serial.print("Message arrived on topic: ");
//   Serial.print(topic);
//   Serial.print(". Message: ");
//   String messageTemp;
  
//   for (int i = 0; i < length; i++) {
//     Serial.print((char)message[i]);
//     messageTemp += (char)message[i];
//   }
//   Serial.println();

//   // Feel free to add more if statements to control more GPIOs with MQTT

//   // If a message is received on the topic esp32/output, you check if the message is either "on" or "off". 
//   // Changes the output state according to the message
//   if (String(topic) == "esp32/output") {
//     Serial.print("Changing output to ");
//     if(messageTemp == "on"){
//       Serial.println("on");
//       digitalWrite(ledPin, HIGH);
//     }
//     else if(messageTemp == "off"){
//       Serial.println("off");
//       digitalWrite(ledPin, LOW);
//     }
//   }
// }

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Subscribe
      //client.subscribe("esp32/output");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  float humi = dht.readHumidity();
  float temp = dht.readTemperature();
  char tempString[8];
  dtostrf(temp, 6, 2, tempString);
  Serial.print("Temperature for first fridge: ");
  Serial.println(tempString);
  client.publish("Frig1/temperature", tempString);

  char tempString2[8];
  dtostrf(temp + 1.5, 6, 2, tempString2); // adding a temp of 1,5 to show the difference because i am onluy using one dht sensor
  Serial.println("Temperature for second fridge: ");
  Serial.println(tempString2);
  client.publish("Frig2/temperature", tempString2);

  //humidity = bme.readHumidity();
    
    // Convert the value to a char array
  char humString[8];
  dtostrf(humi, 6, 2, humString);
  Serial.print("Humidity for first fridge: ");
  Serial.println(humString);
  client.publish("Frig1/humidity", humString);

  char humString2[8];
  dtostrf(humi + 2, 6, 2, humString2); // +2 to humidity to see a difference
  Serial.print("Humidity for second fridge: ");
  Serial.println(humString2);
  client.publish("Frig2/humidity", humString2);



  // long now = millis();
  // if (now - lastMsg > 5000) {
  //   lastMsg = now;
    
  //   // Temperature in Celsius
  //   temperature = bme.readTemperature();   
  //   // Uncomment the next line to set temperature in Fahrenheit 
  //   // (and comment the previous temperature line)
  //   //temperature = 1.8 * bme.readTemperature() + 32; // Temperature in Fahrenheit
    
  //   // Convert the value to a char array
  //   char tempString[8];
  //   dtostrf(temperature, 1, 2, tempString);
  //   Serial.print("Temperature: ");
  //   Serial.println(tempString);
  //   client.publish("esp32/temperature", tempString);

  //   humidity = bme.readHumidity();
    
  //   // Convert the value to a char array
  //   char humString[8];
  //   dtostrf(humidity, 1, 2, humString);
  //   Serial.print("Humidity: ");
  //   Serial.println(humString);
  //   client.publish("esp32/humidity", humString);
  // }
  client.publish("vanier", "I am ESP32");
  delay(2000);
}
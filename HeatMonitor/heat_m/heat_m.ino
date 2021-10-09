#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

DHTesp dht;
const int DHT22Pin = 4;
 
const char* SSID = "LSRCT";
const char* PSK = "83067046472468411597";
const char* MQTT_BROKER = "192.168.178.27";
 
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;



 
void setup() {
    initDHT();
    Serial.begin(115200);
    setup_wifi();
    client.setServer(MQTT_BROKER, 1883);
}

// sets up relayPins and the res ground pin
void initDHT(){
  dht.setup(DHT22Pin, DHTesp::DHT22); // Connect DHT sensor to GPIO 17
  }
 
void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(SSID);
 
    WiFi.begin(SSID, PSK);
 
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
 
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}
 
void reconnect() {
    while (!client.connected()) {
        Serial.println("Reconnecting MQTT...");
        if (!client.connect("ESP8266Client")) {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
    Serial.println("MQTT Connected...");
}
 
void loop() {
    if (!client.connected()) {
        reconnect();
    }
    //client.loop();
    float temperature = dht.getTemperature();
    float humidity = dht.getHumidity();
    char BrokerMsg[8];
    snprintf(BrokerMsg, 8, "%.2f", temperature);
    client.publish("AN/temp", BrokerMsg);
    snprintf(BrokerMsg, 8, "%.2f", humidity);
    client.publish("AN/humid", BrokerMsg);
    Serial.println("test");
    delay(60000);
}

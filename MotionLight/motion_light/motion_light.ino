#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "USDS.h"

// PIN constants to avoid confusion
static const uint8_t D0   = 16;
static const uint8_t D1   = 5;
static const uint8_t D2   = 4;
static const uint8_t D3   = 0;
static const uint8_t D4   = 2;
static const uint8_t D5   = 14;
static const uint8_t D6   = 12;
static const uint8_t D7   = 13;
static const uint8_t D8   = 15;
static const uint8_t D9   = 3;
static const uint8_t D10 = 1;
 
const char* SSID = "LSRCT";
const char* PSK = "83067046472468411597";
const char* MQTT_BROKER = "192.168.178.27";
 
WiFiClient espClient;
PubSubClient MQTTclient(espClient);
USDS distSensor(D2, D1);
long lastMsg = 0;
char msg[8];
double last_dist = 0;
double now_dist = 0;
double dist_diff = 0;

 
void setup() {
    Serial.begin(115200);
    setup_wifi();
    MQTTclient.setServer(MQTT_BROKER, 1883);
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
    while (!MQTTclient.connected()) {
        Serial.println("Reconnecting MQTT...");
        if (!MQTTclient.connect("ESP8266Client")) {
            Serial.print("failed, rc=");
            Serial.print(MQTTclient.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
    Serial.println("MQTT Connected...");
}

void loop() {
    if (!MQTTclient.connected()) {
        reconnect();
    }
    MQTTclient.loop();
    last_dist = now_dist;
    now_dist = 0;
    for(int i=0;i<5;i++){
      now_dist = now_dist + distSensor.getDist();
      delay(100);
    }
    now_dist = now_dist / 5.0;
    dist_diff = abs(last_dist-now_dist);
    snprintf(msg, 8, "%.1f", dist_diff);
    MQTTclient.publish("AN/ultrasonic_1", msg);
    //delay(100);
}

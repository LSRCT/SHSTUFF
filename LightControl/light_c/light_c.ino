#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const int relayPin = 14;
 
const char* SSID = "FRITZ!Box 7560 BL";
const char* PSK = "77581211526824077024";
const char* MQTT_BROKER = "192.168.178.32";
 
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;



 
void setup() {
    initRelays();
    Serial.begin(115200);
    setup_wifi();
    client.setServer(MQTT_BROKER, 1883);
    client.setCallback(callback);
}

// sets up relayPins and the res ground pin
void initRelays(){
  // set up the relay to be off on default for safety.
  pinMode(relayPin,OUTPUT);
  digitalWrite(relayPin, LOW);
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

void handleMsg(char* msg){
    if(strcmp(msg,"ON")==0){
        Serial.println("Relay ON");
        digitalWrite(relayPin, HIGH);
    }
    else if(strcmp(msg,"OFF")==0){
       Serial.println("Relay OFF");
        digitalWrite(relayPin, LOW);
    }
  }
 
void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Received message [");
    Serial.print(topic);
    Serial.print("] ");
    char msg[length+1];
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
        msg[i] = (char)payload[i];
    }
    Serial.println();
 
    msg[length] = '\0';
    handleMsg(msg);
    Serial.println(msg);
 

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
    client.subscribe("lightswitch_1");
    Serial.println("MQTT Connected...");
}
 
void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}

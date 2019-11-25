#include <PubSubClient.h>
#include "AsyncWait.h"
#include <ESP8266WiFi.h>
#include "globals.h"
#include "SetupWifi.h"
#include "secure_credentials.h"

#define MQTT_BROKER_PORT 8883
#define MQTT_BROKER_IP 192,168,1,83

SetupWifi setupWifi(
    STASSID, STAPSK,
    CA_CERT_PROG, CLIENT_CERT_PROG, CLIENT_KEY_PROG
);

const char* mqtt_server = MQTT_SERVER;
IPAddress broker_ip(MQTT_BROKER_IP);

const String TOPIC_ZONE_ON("irrigation/zone/on");
const String TOPIC_ZONE_OFF("irrigation/zone/off");
const String TOPIC_ZONE_STATUS("irrigation/zone/status");

PubSubClient pubsubClient(setupWifi.getWiFiClient());

bool verify_tls() {
  BearSSL::WiFiClientSecure espClient = setupWifi.getWifiSecureClient();
  return espClient.connect(broker_ip, MQTT_BROKER_PORT);
}

void callback(char* topic, byte* payload, unsigned int length) {
    String topicStr;
    String payloadStr;

    for (int i = 0; topic[i]; i++) {
        topicStr += topic[i];
    }

    for (int i = 0; i < length; i++) {
        payloadStr += (char)payload[i];
    }

    DEBUG_LOGLN("");
    DEBUG_LOG("Message arrived - [");
    DEBUG_LOG(topicStr);
    DEBUG_LOG("] ");
    DEBUG_LOGLN(payloadStr);
}

void reconnectToMQTT() {
  if (pubsubClient.connected()) {
    return;
  }

  // Create a random client ID
  String clientId = "ESP8266Client-";
  clientId += String(random(0xffff), HEX);

//   static AsyncWait waitToRetry;
//   if (waitToRetry.isWaiting(currentMilliSec)) {
//     return;
//   }

  DEBUG_LOG("Attempting MQTT connection...");

  if (pubsubClient.connect(clientId.c_str(), "mx", "coucou")) {
    DEBUG_LOGLN("connected");

    pubsubClient.subscribe(TOPIC_ZONE_ON.c_str());
    DEBUG_LOG("Subcribed to: ");
    DEBUG_LOGLN(TOPIC_ZONE_ON);

    char *hello = "Hello from esp8266";
    pubsubClient.publish("presence", hello);
  } else {
    DEBUG_LOGLN(" try again in some seconds. rc=");
    DEBUG_LOGLN(pubsubClient.state());

    if (pubsubClient.state() == MQTT_CONNECT_FAILED) {
        DEBUG_LOGLN("the network connection failed...");
    }

    delay(5000);
    // waitToRetry.startWaiting(currentMilliSec, 5000);
  }
}

void setup() {
  #ifdef DEBUG
  Serial.begin(115200);
  #endif

  setupWifi.setupWifi();

  pubsubClient.setServer(broker_ip, 8883);
  pubsubClient.setCallback(callback);
}

void loop() {
    setupWifi.loopWifi();

    if (!setupWifi.isReadyForProcessing()) {
        // The WiFi is not ready yet so
        // don't do any further processing.
        return;
    }

    if (!pubsubClient.connected()) {
        // Reconnect if connection is lost for example.
        // MilliSec currentMilliSec = millis();
        reconnectToMQTT();
    }

    pubsubClient.loop();
}

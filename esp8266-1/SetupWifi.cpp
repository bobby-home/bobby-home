#include <ESP8266WiFi.h>
#include <time.h>
#include "globals.h"
#include "SetupWifi.h"

#define NTP_SERVERS "0.nl.pool.ntp.org", "1.nl.pool.ntp.org", "2.nl.pool.ntp.org"
#define UTC_OFFSET +1


// Set time via NTP, as required for x.509 validation
void SetupWifi::setClock() {

    configTime(UTC_OFFSET * 3600, 0, NTP_SERVERS);
    setClock_status = STARTED;
    DEBUG_LOG("Waiting for NTP time sync: ");
    setClock_AsyncWait.startWaiting(millis(), 1000); // Log every 1 second.
    // Asynchronously wait for network response via checkClockStatus().
}


// Check Clock Status and update 'setClock_status' accordingly.
void SetupWifi::checkClockStatus() {
    time_t now = time(nullptr);
    if(now < 8 * 3600 * 2) {
        // The NTP request has not yet completed.
        if (!setClock_AsyncWait.isWaiting(millis())) {
            DEBUG_LOG(".");
            setClock_AsyncWait.startWaiting(millis(), 1000); // Log every 1 second.
        }
        return;
    }

    // The NTP request has now completed.
    setClock_status = SUCCESS;

    #ifdef DEBUG
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    DEBUG_LOGLN("");
    DEBUG_LOG("Current time: ");
    DEBUG_LOGLN(asctime(&timeinfo));
    #endif //DEBUG
}


String SetupWifi::getMacAddress() {
    byte mac[6];
    String macStr;

    WiFi.macAddress(mac);
    macStr = String(mac[0], HEX) + ":"
           + String(mac[1], HEX) + ":"
           + String(mac[2], HEX) + ":"
           + String(mac[3], HEX) + ":"
           + String(mac[4], HEX) + ":"
           + String(mac[5], HEX);
    
    return macStr;
}


// Connect to WiFi network.
void SetupWifi::setupWifi() {
    DEBUG_LOGLN("");
    DEBUG_LOG("MAC ");
    DEBUG_LOGLN(getMacAddress());
    DEBUG_LOG("Connecting to ");
    DEBUG_LOGLN(ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    while (WiFi.waitForConnectResult() != WL_CONNECTED) {
        DEBUG_LOGLN("Connection Failed! Rebooting...");
        delay(5000);
        ESP.restart();
    }

    DEBUG_LOGLN("WiFi connected");
    DEBUG_LOG("IP ");
    DEBUG_LOG(WiFi.localIP());
    randomSeed(micros());

    setClock();

    DEBUG_LOGLN("Ready.");
}


void SetupWifi::loopWifi() {
    // Prevent ALL other actions here until the clock as been set by NTP.
    if (setClock_status < FINISHED) {
        checkClockStatus();
        return;
    }
}

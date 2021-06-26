#include "SPIFFS.h"
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "esp_camera.h"
#include <Preferences.h>
#include <ArduinoJson.h>

// Allocate a temporary JsonDocument
// Use https://arduinojson.org/v6/assistant to compute the capacity.

Preferences preferences;

WiFiClient espClient;
PubSubClient client(espClient);

const uint16_t size = 1024;

#define MQTT_BROKER_PORT 8883
// #define MQTT_BROKER_IP 192, 168, 1, 14
// IPAddress broker_ip(MQTT_BROKER_IP);

const char *ssid, *password, *mqtt_server, *mqtt_user, *mqtt_port, *mqtt_password, *host_name;
// DynamicJsonDocument CONFIG_JSON(2048);
StaticJsonDocument<2048> CONFIG_JSON;

#define TOPIC_PUBLISH_PICTURE "test/picture"
#define TOPIC_RECV_REGISTERED "registered/alarm"

// <!> will add /<device_id> at the end.
#define TOPIC_CAMERA_MANAGER "status/camera_manager/"

#define CAMERA_MODEL_AI_THINKER
#include "pins.h"

void init_mqtt_camera(String device_id, bool new_device);
void publish_camera_status(bool status);

const int send_picture_period_ms = 1000;
unsigned long time_now_send_picture = 0;

String device_id = "";
bool run_camera = false;
uint16_t bufferSize = client.getBufferSize();

typedef int32_t conf_err_t;

#define CONF_OK          0
#define CONF_ERR_FILE_NOT_FOUND 0x101
#define CONF_ERR_START_SPIFFS 0x102


/**
 * @brief Load configuration file to global variables.
 */
conf_err_t load_configuration() {
  if (!SPIFFS.begin()) {
    Serial.println("failed to mount FS");
    return CONF_ERR_START_SPIFFS;
  }

  Serial.println("mounted file system");

  if (SPIFFS.exists("/config.json")) {
    //file exists, reading and loading
    File config_file = SPIFFS.open("/config.json", "r");

    if (config_file) {
      Serial.println("opened config file");
      String  config_string = config_file.readString();

      deserializeJson(CONFIG_JSON, config_string);

      ssid = CONFIG_JSON["ssid"];
      password = CONFIG_JSON["password"];
      mqtt_server = CONFIG_JSON["mqtt_server"];
      host_name = CONFIG_JSON["host_name"];
      mqtt_user = CONFIG_JSON["mqtt_user"];
      mqtt_password = CONFIG_JSON["mqtt_password"];

      config_file.close();
      SPIFFS.end();

      return CONF_OK;
    }
  } else {
    Serial.println("Could not find the file config.json");
    SPIFFS.end();
    return CONF_ERR_FILE_NOT_FOUND;
  }

  SPIFFS.end();
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  Serial.println(password);
  WiFi.mode(WIFI_STA);

  // WiFi.HostName(host_name);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("Mac address: ");
  Serial.println(WiFi.macAddress());
}

void reconnect() {
  bool connected = false;
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (device_id.equals("")) {
      Serial.println("connect without will message because device_id is unkown.");
      connected = client.connect(host_name, mqtt_user, mqtt_password);
    } else {
      char will_topic[100];
      char mqtt_hostname[100];
      const char* id = device_id.c_str();

      snprintf(will_topic, sizeof(will_topic), "status/camera/%s", id);
      snprintf(mqtt_hostname, sizeof(mqtt_hostname), "esp-%s", id);

      Serial.println("connect with will message to sync status.");

      Serial.println(mqtt_hostname);
      Serial.println(mqtt_user);
      Serial.println(mqtt_password);
      Serial.println(will_topic);

      // \x00 = binary of false
      connected = client.connect(mqtt_hostname, mqtt_user, mqtt_password, will_topic, 1, true, "\x00");
    }

    if (connected) {
      Serial.println("connected");
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

esp_err_t camera_deinit() {
  return esp_camera_deinit();
}

esp_err_t camera_init() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = 5;
  config.pin_d1       = 18;
  config.pin_d2       = 19;
  config.pin_d3       = 21;
  config.pin_d4       = 36;
  config.pin_d5       = 39;
  config.pin_d6       = 34;
  config.pin_d7       = 35;
  config.pin_xclk     = 0;
  config.pin_pclk     = 22;
  config.pin_vsync    = 25;
  config.pin_href     = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn     = 32;
  config.pin_reset    = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size   = FRAMESIZE_VGA; // QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
  config.jpeg_quality = 10;           
  config.fb_count     = 1;

  // config.ledc_channel = LEDC_CHANNEL_0;
  // config.ledc_timer = LEDC_TIMER_0;
  // config.pin_d0 = Y2_GPIO_NUM;
  // config.pin_d1 = Y3_GPIO_NUM;
  // config.pin_d2 = Y4_GPIO_NUM;
  // config.pin_d3 = Y5_GPIO_NUM;
  // config.pin_d4 = Y6_GPIO_NUM;
  // config.pin_d5 = Y7_GPIO_NUM;
  // config.pin_d6 = Y8_GPIO_NUM;
  // config.pin_d7 = Y9_GPIO_NUM;
  // config.pin_xclk = XCLK_GPIO_NUM;
  // config.pin_pclk = PCLK_GPIO_NUM;
  // config.pin_vsync = VSYNC_GPIO_NUM;
  // config.pin_href = HREF_GPIO_NUM;
  // config.pin_sscb_sda = SIOD_GPIO_NUM;
  // config.pin_sscb_scl = SIOC_GPIO_NUM;
  // config.pin_pwdn = PWDN_GPIO_NUM;
  // config.pin_reset = RESET_GPIO_NUM;
  // config.xclk_freq_hz = 20000000;
  // config.pixel_format = PIXFORMAT_JPEG;

  // config.fb_count = 1;
  // config.jpeg_quality = 10;
  // config.frame_size = FRAMESIZE_VGA;

  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK) {
    ESP_LOGE(TAG, "Camera Init Failed");
    return err;
  }

  return ESP_OK;
}

void in_device_register(String payload) {
  StaticJsonDocument<1024> CONFIG;
  deserializeJson(CONFIG, payload);
  const char* id = CONFIG["id"];

  if(WiFi.macAddress().equals(id)) {
    Serial.print("\n Got the device_id from bobby core");
    Serial.println(payload);
    const char* device_id = CONFIG["device_id"];
    Serial.println(device_id);

    preferences.putString("device_id", device_id);
    init_mqtt_camera(device_id, true);
  } else {
    Serial.println("Got a device_id but not for me.");
  }
}

void in_camera_status(String payload) {
  StaticJsonDocument<1048> PAYLOAD_JSON;
  deserializeJson(PAYLOAD_JSON, payload);
  Serial.println("handling camera status");

  const bool status = PAYLOAD_JSON["status"];
  Serial.println(payload);
  Serial.println("status: ");
  Serial.println(status);
  run_camera = status;

  if(status) {
    camera_init();
    // let the camera warms up.
    delay(1000);
    publish_camera_status(true);
  } else {
    camera_deinit();
    publish_camera_status(false);
  }
}

void mqtt_callback(String topic, byte* message, unsigned int length) {
  String payload;
  for (int i = 0; i < length; i++) {
    payload += (char)message[i];
  }

  Serial.println("mqtt callback called with topic: ");
  Serial.println(topic);

  if (topic.equals(TOPIC_RECV_REGISTERED)) {
    in_device_register(payload);
  }
  else if (topic.equals(TOPIC_CAMERA_MANAGER + device_id)) {
    in_camera_status(topic);
  }
}

/**
 * @brief Register the device to Bobby core.
 * It is async, Bobby will answer by sending us the attributed `device_id` through mqtt.
 */
void register_device() {
  StaticJsonDocument<1024> payload;

  payload["type"] = "esp32cam";
  payload["id"] = WiFi.macAddress();
  payload["mac_address"] = WiFi.macAddress();

  char buffer[1024];
  serializeJson(payload, buffer);

  Serial.println("No device_id! Get one from the core app.");
  client.subscribe(TOPIC_RECV_REGISTERED);
  client.publish("discover/alarm", buffer, false);
}

void setup() {
  Serial.begin(9600); // Initialize serial communications with the PC
  while (!Serial); // Do nothing if no serial port is opened

  conf_err_t status = load_configuration();
  if (status != CONF_OK) {
    Serial.println("Stop because configuration cannot load.");
    return;
  }

  setup_wifi();

  client.setServer(mqtt_server, MQTT_BROKER_PORT);
  client.setCallback(mqtt_callback);

  // RW-mode (second parameter has to be false).
  preferences.begin("bobby-cam", false);
  device_id = preferences.getString("device_id", "");

  reconnect();

  if (device_id.equals("")) {
    register_device();
  } else {
    Serial.print("\n setup known device_id: ");
    Serial.println(device_id);
    init_mqtt_camera(device_id, false);
  }
}

esp_err_t process_image(camera_fb_t *fb, uint16_t *mqttBufferSize) {
  if (fb->len > *mqttBufferSize) {
    size_t newSize = fb->len + ((20/100) * fb->len);
    bool is_realloc = client.setBufferSize(newSize);
    Serial.printf("\nRealloc buffer size from %zu to %zu\n", fb->len, newSize);

    if (!is_realloc) {
      ESP_LOGE(TAG, "Realloc buffer failed.");
      // don't go any further, mqtt publish won't work.
      return ESP_ERR_NO_MEM;
    } else {
      *mqttBufferSize = client.getBufferSize();
    }
  }

  char buff[100];
  const char* id = device_id.c_str();
  snprintf(buff, sizeof(buff), "ia/picture/%s", id);

  client.publish(buff, fb->buf, fb->len, false);
  return ESP_OK;
}

esp_err_t camera_capture() {
  //acquire a frame
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    ESP_LOGE(TAG, "Camera Capture Failed");
    return ESP_FAIL;
  }

  Serial.printf("\nSize of picture: %zu\n", fb->len);

  esp_err_t processed = process_image(fb, &bufferSize);
  if (processed!= ESP_OK) {
    return processed;
  }

  // return the frame buffer back to the driver for reuse
  esp_camera_fb_return(fb);
  return ESP_OK;
}

void mqtt_loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();
}

/**
 * @brief Inform Bobby the status of the camera.
 */
void publish_camera_status(bool status) {
  String payload = "";

  if (status) {
    payload = "\x01";
  } else {
    payload = "\x00";
  }

  const char* id = device_id.c_str();
  char camera_topic[100];
  snprintf(camera_topic, sizeof(camera_topic), "connected/camera/%s", id);

  client.publish(camera_topic, payload.c_str());
}

void init_mqtt_camera(String device_id, bool new_device) {
  if (new_device) {
    // I need to know if we had to ask bobby core the device_id because will is not set (because device id was unkown when mqtt started)
    // if so, I need to disconnect and reconnect the mqtt client :)
    Serial.println("disconnect mqtt and reconnect it to set the camera will message with the device_id.");
    client.disconnect();
    reconnect();
  }

  const char* id = device_id.c_str();

  char camera_manager_topic[100];
  snprintf(camera_manager_topic, sizeof(camera_manager_topic), "status/camera_manager/%s", id);
  // subscribe to mqtt camera topics to up/off.
  client.subscribe(camera_manager_topic, 1);
}

void camera_loop() {
  if (!run_camera) return;

  if(millis() - time_now_send_picture > send_picture_period_ms) {
    time_now_send_picture = millis();
    camera_capture();
  }
}

void loop() {
  mqtt_loop();
  camera_loop();
}

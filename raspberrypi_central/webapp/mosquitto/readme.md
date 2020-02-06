# Generate keys
## Server
You have to generate server keys for you mosquitto before running the service.
```bash
./mosquitto/generate-keys.sh server
```

## Client
You have to generate one key pairs for each of your clients that will connect to your MQTT server.

```bash
./mosquitto/generate-keys.sh client
```

# Generate user/password
You have to generate user/password for MQTT.

```bash
./mosquitto/generate-password.sh <user>
```

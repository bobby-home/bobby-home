# Generate keys
## Server
```
bash ./generate-CA.sh
```
That will generate three files : `ca.crt, <hostname>.crt, <hostname>.key,`.
Then you have to configure your `mosquittto.conf` to specify these files.

```
cafile /mosquitto/config/certs/ca.crt
keyfile /mosquitto/config/certs/<hostname>.key
certfile /mosquitto/config/certs/<hostname>.crt
```

## Client
Please generate one certificate per client.
```
bash ./generate-CA.sh client <client_name>
```
That will generate `<client_name>.key` and `<client_name>.crt` that you can use. You can delete other files.

## Draft (doesn't work)
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

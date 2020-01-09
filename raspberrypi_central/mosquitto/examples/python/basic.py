import paho.mqtt.client as mqtt

broker_ip = "172.18.0.2"

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        raise ValueError('on_connect failed with code '+rc)

    print("Connected with result code "+str(rc))
    client.subscribe("topic/test")

client = mqtt.Client()

client.username_pw_set('mx', 'coucou')
client.connect(broker_ip, port=1883, keepalive=60)

client.publish("topic/test", "Hello world!")

client.on_connect = on_connect

client.disconnect()

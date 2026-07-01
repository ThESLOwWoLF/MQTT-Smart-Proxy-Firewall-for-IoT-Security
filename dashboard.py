import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TRUSTED_TOPIC = "trusted/#"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print(f"Connected to broker")
        client.subscribe(TRUSTED_TOPIC)
        print(f"Subscribed to safe topic '{TRUSTED_TOPIC}'")
    else:
        print(f"failed to connect return code {rc}")

def on_message(client, userdata, msg):
    print(f"RECEIVED: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "dashboard_client")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()
import paho.mqtt.client as mqtt
import time
import json
import random

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "sensor-01"
TOPIC = "untrusted/sensor-01/temp"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

print(f"SENSOR ({CLIENT_ID}) publishing to{TOPIC}")

try:
    while True:
        # Create a valid payload
        temp = round(random.uniform(20.0, 30.0), 2)
        payload = json.dumps({"value": temp})

        client.publish(TOPIC, payload)
        print(f"SENSOR: Sent '{payload}'")
        time.sleep(5)
except KeyboardInterrupt:
    print("\nSENSOR: Stopped.")
    client.loop_stop()
    client.disconnect()
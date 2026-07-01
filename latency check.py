# --- latency_sensor.py (v2 - 20 Message Limit) ---
# This script sends exactly 20 messages, one per second, with timestamps.

import paho.mqtt.client as mqtt
import time
import json
import sys

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "sensor-01"
MESSAGE_COUNT_LIMIT = 20

if len(sys.argv) != 2 or sys.argv[1] not in ['vanilla', 'proxy']:
    print("Usage: python latency_sensor.py <test_type>")
    print("  test_type: 'vanilla' OR 'proxy'")
    sys.exit(1)

test_type = sys.argv[1]

if test_type == 'vanilla':
    TOPIC = "vanilla/test"
    print(f"SENSOR: Running 'VANILLA' test. Publishing 20 messages to '{TOPIC}'...")
else:
    TOPIC = "untrusted/sensor-01/temp"
    print(f"SENSOR: Running 'M-IDS' test. Publishing 20 messages to '{TOPIC}'...")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

# Give a moment for the connection to establish
time.sleep(1)

for i in range(MESSAGE_COUNT_LIMIT):
    # Create a valid payload that will pass our proxy's rules
    temp = 25.0
    send_time = time.time()  # Get current time in high-precision seconds

    # Add the timestamp to the payload
    payload = json.dumps({
        "value": temp,
        "timestamp": send_time
    })

    client.publish(TOPIC, payload)
    print(f"SENSOR: Sent message {i + 1}/{MESSAGE_COUNT_LIMIT}")
    time.sleep(1)  # Send one message per second

print("\nSENSOR: Test complete. Disconnecting...")
client.loop_stop()
client.disconnect()
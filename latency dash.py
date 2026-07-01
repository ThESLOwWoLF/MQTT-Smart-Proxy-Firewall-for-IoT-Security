# --- latency_dashboard.py (v2 - 20 Message Limit) ---
# This script subscribes to a topic, receives exactly 20 messages,
# and then prints the final average latency and stops.

import paho.mqtt.client as mqtt
import time
import json
import sys

BROKER_HOST = "localhost"
BROKER_PORT = 1883
MESSAGE_COUNT_LIMIT = 20

if len(sys.argv) != 2 or sys.argv[1] not in ['vanilla', 'proxy']:
    print("Usage: python latency_dashboard.py <test_type>")
    print("  test_type: 'vanilla' OR 'proxy'")
    sys.exit(1)

test_type = sys.argv[1]

if test_type == 'vanilla':
    TOPIC_TO_SUBSCRIBE = "vanilla/#"
    print(f"DASHBOARD: Running 'VANILLA' test. Subscribing to '{TOPIC_TO_SUBSCRIBE}'...")
else:
    TOPIC_TO_SUBSCRIBE = "trusted/#"
    print(f"DASHBOARD: Running 'M-IDS' test. Subscribing to '{TOPIC_TO_SUBSCRIBE}'...")

# This list will store all the latency values
latencies = []


def on_connect(client, userdata, flags, rc, properties):
    print(f"DASHBOARD: Connected. Subscribing to '{TOPIC_TO_SUBSCRIBE}'")
    client.subscribe(TOPIC_TO_SUBSCRIBE)


def on_message(client, userdata, msg):
    try:
        # Get the time the message arrived
        receive_time = time.time()

        payload = json.loads(msg.payload.decode())

        # Check if it has our timestamp
        if "timestamp" in payload:
            send_time = payload["timestamp"]

            # Calculate latency in milliseconds
            latency_ms = (receive_time - send_time) * 1000
            latencies.append(latency_ms)

            print(f"  ({len(latencies)}/{MESSAGE_COUNT_LIMIT}) Received message. Latency: {latency_ms:.2f} ms")

        # Check if we have received all 20 messages
        if len(latencies) >= MESSAGE_COUNT_LIMIT:
            client.loop_stop()  # Stop the loop

    except Exception as e:
        print(f"Error processing message: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "dashboard_client")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, 60)

try:
    client.loop_forever()  # This loop will be stopped by on_message
except KeyboardInterrupt:
    print("\nDASHBOARD: Test interrupted.")
finally:
    # This block will run after loop_forever() stops
    client.disconnect()

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        print("\n" + "=" * 30)
        print("--- FINAL LATENCY RESULTS ---")
        print(f"Total Messages: {len(latencies)}")
        print(f"Average Latency: {avg_latency:.2f} ms")
        print(f"Min Latency:     {min_latency:.2f} ms")
        print(f"Max Latency:     {max_latency:.2f} ms")
        print("=" * 30)
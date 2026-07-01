# --- attacker.py (The "Attack" Tool v2) ---
import paho.mqtt.client as mqtt
import time
import json
import sys

BROKER_HOST = "localhost"
BROKER_PORT = 1883


def show_usage():
    print("Usage: python attacker.py <attack_type>")
    print("Attack Types:")
    print("  topic  - (Rule 1) Tries to publish to an unauthorized admin topic.")
    print("  payload - (Rule 2) Tries to publish bad JSON to an *allowed* topic.")
    print("  spam - (Rule 3) Tries to flood an allowed topic (Rate Limit). [cite: 1842]")
    print("  long_topic  - (Rule 4) Tries to publish to a topic with a >1024 char name. ")
    sys.exit(1)


if len(sys.argv) != 2:
    show_usage()

attack_type = sys.argv[1]

# --- Attack 1: Topic Authorization ---
if attack_type == "topic":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "hacker-01")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    topic = "untrusted/hacker-01/admin_reboot"
    payload = "reboot_all"
    print(f"ATTACKER: [TOPIC ATTACK] Trying to publish '{payload}' to '{topic}'...")
    client.publish(topic, payload)
    print("ATTACKER: Message sent")
    client.disconnect()

# --- Attack 2: Payload Validation (Bad JSON) ---
elif attack_type == "payload":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "sensor-01")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    topic = "untrusted/sensor-01/temp"
    payload = "this is not json"
    print(f"ATTACKER: [PAYLOAD ATTACK] Trying to publish '{payload}' to '{topic}'...")
    client.publish(topic, payload)
    print("ATTACKER: Message sent")
    client.disconnect()

# --- Attack 3: Payload Validation (Out of Range) ---
elif attack_type == "range":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "sensor-01")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    topic = "untrusted/sensor-01/temp"
    payload = json.dumps({"value": 999})
    print(f"ATTACKER: [RANGE ATTACK] Trying to publish '{payload}' to '{topic}'")
    client.publish(topic, payload)
    print("ATTACKER: Message sent")
    client.disconnect()

# --- Attack 4: Anomaly Detection (Rate Limit) ---
elif attack_type == "spam":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "spammer-01")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    topic = "untrusted/sensor-01/temp"
    payload = json.dumps({"value": 42})
    print(f"ATTACKER: [SPAM ATTACK] Flooding topic '{topic}'... Press Ctrl+C to stop.")
    try:
        count = 0
        while True:
            client.publish(topic, payload)
            count += 1
            print(f"ATTACKER: Sent message {count}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nATTACKER: Stopping ")
        client.loop_stop()
        client.disconnect()

# --- NEW ATTACK 5: Malformed Packet (Long Topic) ---
elif attack_type == "long_topic":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "attacker-01")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    long_name = "a" * 1100
    topic = f"untrusted/attacker-01/{long_name}"
    payload = "crash"
    print(f"ATTACKER: [LONG TOPIC ATTACK] Trying to publish to a topic with {len(topic)} chars ")
    client.publish(topic, payload)
    print("ATTACKER: Message sent")
    client.disconnect()

else:
    show_usage()
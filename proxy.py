import paho.mqtt.client as mqtt
import json
import time

TOPIC_RULES = {
    "sensor-01": ["untrusted/sensor-01/temp"],
    "spammer-01": ["untrusted/sensor-01/temp"],
    "attacker-01": ["untrusted/attacker-01/long_topic"]
}

PAYLOAD_SCHEMAS = {
    "untrusted/sensor-01/temp": {
        "keys": ["value"],
        "types": {"value": (int, float)},
        "range": {"value": (0, 100)}
    }
}

CLIENT_TRACKER = {}
TIME_WINDOW_SEC = 10
MESSAGE_LIMIT = 5

MAX_TOPIC_LENGTH = 1024

BROKER_HOST = "localhost"
BROKER_PORT = 1883
proxy_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "smart_proxy_firewall")


def check_rate_limit(client_id):
    """Checks if a client is sending too many messages."""
    current_time = time.time()
    if client_id not in CLIENT_TRACKER:
        CLIENT_TRACKER[client_id] = []

    timestamps = CLIENT_TRACKER[client_id]
    valid_timestamps = [t for t in timestamps if current_time - t < TIME_WINDOW_SEC]

    if len(valid_timestamps) >= MESSAGE_LIMIT:
        CLIENT_TRACKER[client_id] = valid_timestamps
        return False

    valid_timestamps.append(current_time)
    CLIENT_TRACKER[client_id] = valid_timestamps
    return True


def check_topic_auth(client_id, topic):
    """Checks if the client is allowed to publish to this topic."""
    return client_id in TOPIC_RULES and topic in TOPIC_RULES.get(client_id, [])


def check_payload_valid(topic, payload_str):
    """Checks if payload follows the defined schema."""
    if topic not in PAYLOAD_SCHEMAS:
        return True

    schema = PAYLOAD_SCHEMAS[topic]
    try:
        data = json.loads(payload_str)
        if (any(key not in data for key in schema["keys"]) or
            any(not isinstance(data[key], schema["types"][key]) for key in schema["types"]) or
            any(not (schema["range"][key][0] <= data[key] <= schema["range"][key][1]) for key in schema["range"])):
            return False
        return True
    except Exception:
        return False


def check_malformed_packet(topic):
    """Checks for malformed or excessively long MQTT topics."""
    return len(topic) <= MAX_TOPIC_LENGTH


def on_connect(client, userdata, flags, rc, properties):
    """Runs when the proxy connects to the broker."""
    if rc == 0:
        print(f"PROXY: Connected to broker at {BROKER_HOST}.")
        client.subscribe("untrusted/#")
        print("PROXY: Subscribed to 'untrusted/#'.")
    else:
        print(f"PROXY: Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """Main firewall logic applied to every intercepted message."""
    topic = msg.topic
    payload_str = msg.payload.decode()

    try:
        client_id = topic.split('/')[1]
    except IndexError:
        print(f"DENY: Malformed topic '{topic}'. Dropping.")
        return

    if not check_malformed_packet(topic):
        print(f"DENY: '{client_id}' - Malformed Packet.")
        return
    if not check_rate_limit(client_id):
        print(f"DENY: '{client_id}' - Rate Limit Exceeded.")
        return
    if not check_topic_auth(client_id, topic):
        print(f"DENY: '{client_id}' - Unauthorized Topic.")
        return
    if not check_payload_valid(topic, payload_str):
        print(f"DENY: '{client_id}' - Invalid Payload.")
        return

    trusted_topic = topic.replace("untrusted/", "trusted/", 1)
    print(f"ALLOW: '{client_id}' -> '{trusted_topic}'")
    proxy_client.publish(trusted_topic, payload_str)


print("Starting Smart Proxy Firewall")
proxy_client.on_connect = on_connect
proxy_client.on_message = on_message

try:
    proxy_client.connect(BROKER_HOST, BROKER_PORT, 60)
    proxy_client.loop_forever()
except ConnectionRefusedError:
    print("FATAL ERROR: Could not connect to Mosquitto broker.")
except Exception as e:
    print(f"Unexpected error: {e}")

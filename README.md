# MQTT Smart Proxy Firewall for IoT Security

A Python-based smart proxy firewall that enhances the security of MQTT-based IoT networks by inspecting, validating, and filtering traffic before it reaches the MQTT broker.

## Features

- Real-time MQTT traffic inspection
- Topic-based access control
- JSON payload validation
- Rate limiting to prevent flooding attacks
- Detection and filtering of malformed MQTT packets
- Secure forwarding of authorized messages

## Technologies Used

- Python
- MQTT
- paho-mqtt
- JSON

## Installation

Clone the repository:

```bash
git clone https://github.com/ThESLOwWoLF/MQTT-Smart-Proxy-Firewall-for-IoT-Security.git
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the firewall:

```bash
python firewall.py
```

Run the publisher and subscriber clients as required:

```bash
python publisher.py
python subscriber.py
```

## Future Improvements

- TLS/SSL encrypted MQTT communication
- User authentication and authorization
- Machine learning-based anomaly detection
- Web dashboard for monitoring firewall activity

## Author

**Sudhan Shankar**

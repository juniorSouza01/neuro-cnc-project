# backend-brain/src/mqtt_bridge.py
import paho.mqtt.client as mqtt
import json
import requests
from time import sleep

# Conecta ao Mosquitto e encaminha para a API FastAPI local
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Envia para a própria API (loopback)
        requests.post("http://localhost:8000/telemetry", json=payload)
    except Exception as e:
        print(e)

client = mqtt.Client()
client.on_message = on_message
client.connect("mosquitto", 1883, 60)
client.subscribe("machine/okuma01/telemetry")
client.loop_forever()
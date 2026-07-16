import os
from dotenv import load_dotenv

load_dotenv()


MQTT_BROKER = os.getenv(
    "MQTT_BROKER",
    "192.168.1.170"
)

MQTT_PORT = int(
    os.getenv(
        "MQTT_PORT",
        1883
    )
)

REQUEST_TOPIC = "query/request"
RESPONSE_TOPIC = "query/response"


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:1b"
)
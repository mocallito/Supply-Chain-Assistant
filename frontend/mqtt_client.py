import json
import uuid
import threading

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    REQUEST_TOPIC,
    RESPONSE_TOPIC,
)


responses = {}


def on_message(client, userdata, msg):

    payload = json.loads(
        msg.payload.decode()
    )

    request_id = payload["request_id"]

    responses[request_id] = payload


client = mqtt.Client()

client.on_message = on_message


client.connect(
    MQTT_BROKER,
    MQTT_PORT
)

client.subscribe(
    RESPONSE_TOPIC
)


thread = threading.Thread(
    target=client.loop_forever,
    daemon=True,
)

thread.start()


def retrieve_context(
    question: str,
    top_k: int = 5
):

    request_id = str(uuid.uuid4())

    message = {
        "request_id": request_id,
        "query": question,
        "top_k": top_k,
    }

    client.publish(
        REQUEST_TOPIC,
        json.dumps(message),
    )


    while request_id not in responses:
        pass


    response = responses.pop(request_id)

    return response
import json
import time
import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PORT
from retrieval import RetrievalService

start_time = time.time()
retriever = RetrievalService()
print("Warming up time ", time.time()-start_time)

def on_connect(client, userdata, flags, rc):

    print("Connected")

    client.subscribe("query/request")


def on_message(client, userdata, msg):

    request = json.loads(msg.payload.decode())

    context = retriever.retrieve(
        query=request["query"],
        # filters=request.get("filters"),
        top_k=request.get("top_k", 5),
    )
    
    response = {
        "request_id": request["request_id"],
        **context,
    }

    client.publish(
        "query/response",
        json.dumps(response),
    )


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message


def start():

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
    )

    client.loop_forever()

import json
import uuid
import paho.mqtt.client as mqtt

from config import MQTT_BROKER


response = None



def on_message(
    client,
    userdata,
    msg
):

    global response

    response = json.loads(
        msg.payload.decode()
    )



def retrieve_context(
    question: str,
    top_k: int = 5
):

    global response

    response = None


    client = mqtt.Client()

    client.on_message = on_message


    client.connect(
        MQTT_BROKER
    )


    request_id = str(uuid.uuid4())

    topic = (
        "query/response"
    )


    client.subscribe(
        topic
    )

    message = {
        "request_id": request_id,
        "query": question,
        "top_k": top_k,
    }


    client.publish(
        "query/request",
        json.dumps(message)
    )


    while response is None:

        client.loop(
            timeout=1
        )


    client.disconnect()


    return response

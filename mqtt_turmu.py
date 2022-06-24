# imports for mqtt
from paho.mqtt import client as mqtt_client
import ssl

# import for functionality
import random
import time
from datetime import datetime
import json
import map_object as mo


def load_default_params():
    broker = 'show.manufacturing.tecnalia.dev'
    port = 8883
    client_id = f'maty_python-{random.randint(0, 1000)}'
    username = 'tecnalia'
    password = 't3cn4l1420A'
    ca_certs_path = "./tecnalia_certs/ca.crt"
    certfile_path = "./tecnalia_certs/client.crt"
    keyfile_path = "./tecnalia_certs/client.key"
    return broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path


def connect_mqtt(broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.tls_set(ca_certs=ca_certs_path,
                   certfile=certfile_path,
                   keyfile=keyfile_path,
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLS,
                   ciphers=None)
    client.tls_insecure_set(True)
    client.connect(broker, port)
    return client


def publish(client, topic):
    msg_count = 0
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1


def publish_object(client, topic, object_as_json_string):
    msg = object_as_json_string
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 1:
        print("Error. Couldn't publish message")


def subscribe(client: mqtt_client, topic, current_full_map, candidate_map):
    i = 0
    def on_message(client, userdata, msg, i):
        i += 1
        message_dict = parse_message(message=msg)

        try:
            # get timestamp
            # timestamp = datetime.strptime(message_dict["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")

            # create object from read data
            mo.Object

        except Exception as e:
            print(e)
            print("The message was:")
            print(msg)
            pass

    client.subscribe(topic)
    client.on_message = on_message

    # TODO introduce new loop here


def parse_message(message):
    msg_raw = message.payload.decode()
    msg_clean = msg_raw.replace("\n  ", "").replace("\n", "").replace('""', '", "')
    msg_dict = json.loads(msg_clean)
    return msg_dict

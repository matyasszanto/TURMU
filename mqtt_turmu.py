# imports for mqtt
from paho.mqtt import client as mqtt_client
import ssl

# import for functionality
import random
import time


def load_default_params():
    broker = 'show.manufacturing.tecnalia.dev'
    port = 8883
    client_id = f'maty_python-{random.randint(0, 1000)}'
    username = 'tecnalia'
    password = 't3cn4l1420A'
    ca_certs_path = "./tecnalia_certs/tecnalia_local_ca.crt"
    certfile_path = "./tecnalia_certs/tecnalia_local_client.crt"
    keyfile_path = "./tecnalia_certs/tecnalia_local_client.key"
    return broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path


def connect_mqtt(broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    mqtt_client.Client()
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


def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Received \n{msg.payload.decode()}\nfrom `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message

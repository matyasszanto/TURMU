# imports for mqtt
import numpy as np
from paho.mqtt import client as mqtt_client
import ssl

# import for functionality
import random
from datetime import datetime
import json
import map_obstacle as mo


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


def publish_obstacle(client, topic, obstacle):
    msg = obstacle.as_json()
    result = client.publish(topic, msg)
    status = result[0]
    if status == 1:
        print("Error. Couldn't publish message")


def publish_obstacles(client, topic, obstacles):
    msg = json.dumps(obstacles)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 1:
        print("Error. Couldn't publish message")


def subscribe(client: mqtt_client, topic, obstacles=None, timestamps=None, sensor_locations=None):

    if obstacles is None:
        obstacles = []
    if timestamps is None:
        timestamps = []
    if sensor_locations is None:
        sensor_locations = []

    def on_message(client, userdata, msg):
        message_dict = parse_message(message=msg)
        try:
            if "obstacles" in message_dict:
                for obstacle_dict in message_dict["obstacles"]:
                    obstacle_ = mo.obstacle_object_from_mqtt_payload_obstacle_as_dict(obstacle_dict)
                    obstacles.append(obstacle_)

            if "obstacleId" in message_dict:
                # create obstacle from read data if the message is for an observed obstacle
                """
                {"obstacleId": obstacle_id,"type": obstacle_type, "latitude": lat, "longitude": long,
                 "speed": speed, "width": width, "length": length, "observations": no. of observations}
                """
                obstacle_ = mo.obstacle_object_from_mqtt_payload_obstacle_as_dict(message_dict)
                obstacles.append(obstacle_)
            elif "vehicleId" in message_dict:
                # read sensor location and timestamp from ego-vehicle if the message isf for and ego-vehicle
                timestamps.append(message_dict["timestamp"])
                sensor_locations.append([message_dict["latitude"], message_dict["longitude"]])

        except Exception as e:
            print(e)
            print("The message was:")
            print(msg)
            pass

    client.subscribe(topic)
    client.on_message = on_message


def parse_message(message):
    msg_raw = message.payload.decode()
    msg_clean = msg_raw.replace("\n  ", "").replace("\n", "").replace('""', '", "')
    msg_dict = json.loads(msg_clean)
    return msg_dict

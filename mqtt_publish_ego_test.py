import datetime
import json
import random
import time

import mqtt_turmu
import map_obstacle as mo


def run():
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    topic = "testtopic/egovehicle"

    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path
                                     )

    msg_dict = {"vehicleId": 0,
                # "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latitude": 10,
                "longitude": 10,
                "speed": 3,
                "acceleration": 1.5,
                "yaw": 0.0,
                "yawRate": 0.0,
                "length": 3,
                "width": 1.8
                }

    msg = json.dumps(msg_dict, indent=4, default=str)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 1:
        print("Error. Couldn't publish message")

    client.disconnect()


if __name__ == "__main__":
    run()

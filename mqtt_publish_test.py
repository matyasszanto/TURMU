import datetime
import json
import random
import time

import mqtt_turmu
import map_obstacle as mo


def run(like: [mo.Obstacle] = None, number_of_obstacles=3, latitude_random_radius=10, longitude_random_radius=10):
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    topic = "testtopic/matyas"
    topic = "iotac/Twizy-1/obstacles"
    topic = "iotac/VirtualVehicle-1/obstacles"

    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path
                                     )

    obsts = mo.generate_default_obstacles_list(number_of_obstacles=number_of_obstacles,
                                               number_of_observations=1,
                                               types=["obstacle"],
                                               uniform=True,
                                               )

    obst_dicts_array = []

    for obst in obsts:
        obst_dicts_array.append(obst.as_dict())

    message_dict = {"obstacles": obst_dicts_array,
                    "sensor_latitude": random.uniform(-latitude_random_radius, latitude_random_radius),
                    "sensor_longitude": random.uniform(-longitude_random_radius, longitude_random_radius)
                    }

    client.publish(topic, json.dumps(message_dict, indent=4))

    client.disconnect()
    print("publish_done")


if __name__ == "__main__":
    while True:
        run(number_of_obstacles=1,
            latitude_random_radius=0,
            longitude_random_radius=0,
            )
        time.sleep(1)

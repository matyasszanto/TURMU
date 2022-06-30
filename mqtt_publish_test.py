import datetime
import json
import random
import time

import mqtt_turmu
import map_obstacle as mo


def run(like: [mo.Obstacle] = None, number_of_obstacles=3):
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    topic = "testtopic/matyas"

    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path
                                     )

    mo.turmu_offline_mode_publish(client=client,
                                  topic=topic,
                                  number_of_obstacles=number_of_obstacles,
                                  types=["other"],
                                  like=like)

    obsts = mo.generate_default_obstacles_list(number_of_obstacles=number_of_obstacles,
                                               number_of_observations=1,
                                               types=["other"]
                                               )

    obsts_dict_array = []

    for obst in obsts:
        obsts_dict_array.append(obst.as_dict())

    obsts_dict = {"obstacles": json.dumps(obsts_dict_array)}

    obsts_json = json.dumps(obsts_dict, indent=4, default=str)

    mqtt_turmu.publish_obstacles(client, topic, obsts_json)



    client.disconnect()


if __name__ == "__main__":
    run(number_of_obstacles=2)

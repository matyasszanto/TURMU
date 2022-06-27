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

    mo.turmu_offline_mode_publish(client=client, topic=topic, number_of_obstacles=3)
    client.disconnect()


if __name__ == "__main__":
    run()

import random
import time

import mqtt_turmu

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

for i in range(10):
    client.loop(1)
    mqtt_turmu.subscribe(client, topic, current_full_map=None, candidate_map=None)
    print(f"loop{i} done")
    time.sleep(1)

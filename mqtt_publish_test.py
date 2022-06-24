import datetime
import json
import random
import time

import mqtt_turmu
import map_object as mo

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

client.loop_start()
time.sleep(1)
mo.turmu_offline_mode_publish(3, client)
client.disconnect()



import random

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

client.loop_start()

mqtt_turmu.subscribe(client, topic)

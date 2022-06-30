import random
import time

import map_obstacle
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

obstacles = []
ego = map_obstacle.Egovehicle()

while len(obstacles) == 0:
    client.loop(10)
    mqtt_turmu.subscribe(client=client, topic=topic, obstacles=obstacles)

print("első üzenet megvan")
for obst in obstacles:
    obst.print()

"""
while len(ego.timestamps) == 0:
    client.loop(0)
    mqtt_turmu.subscribe(client=client, topic=topic, sensor_locations=ego.sensor_locations, timestamps=ego.timestamps)

print("második üzenet megvan")
print(ego.sensor_locations)
"""

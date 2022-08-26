import time
import json

import map_obstacle as mo
import mqtt_turmu
import show_obstacles

if __name__ == "__main__":

    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    topic = "testtopic/matyas"
    topic = "iotac/Twizy-1/obstacles"
    topic = "iotac/VirtualVehicle-1/obstacles"
    # topic = "iotac/planner"

    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path
                                     )

    f = open("real_test.json")
    full_run_json = json.load(f)
    for publication in full_run_json:
        # Obsts = []
        # for obst in publication["obstacles"]:
        #     Obst = mo.obstacle_object_from_mqtt_payload_obstacle_as_dict(obst)
        #     Obsts.append(Obst)
        #
        # show_obstacles.plot_obstacles(Obsts)
        client.publish(topic, json.dumps(publication))
        time.sleep(0.3)

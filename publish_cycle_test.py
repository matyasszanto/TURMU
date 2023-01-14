import datetime
import time
import json

import map_obstacle as mo
import mqtt_turmu
import visualize_obstacles

import numpy as np
import pandas as pd

if __name__ == "__main__":

    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    # topic = "testtopic/matyas"
    # topic = "iotac/Twizy-1/obstacles"
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

    # f = open("real_test.json")
    f = open("performance_test/perf_test.json")
    full_run_json = json.load(f)

    plot = False
    if plot:
        max_step_map = 3000
        max_obstacles_map = 50

        max_step = (max_step_map if max_step_map < len(full_run_json) else len(full_run_json))

        lats, longs = np.array([]), np.array([])
        for publication in full_run_json[:max_step]:
            max_obstacles = max_obstacles_map if max_obstacles_map < len(
                publication["obstacles"]
            ) else len(
                publication["obstacles"]
            )

            obsts = publication["obstacles"][:max_obstacles_map]
            obst_lats = list(o["latitude"] for o in obsts)
            obst_longs = list(o["longitude"] for o in obsts)
            lats = np.append(lats, [lat for lat in obst_lats])
            longs = np.append(longs, [long for long in obst_longs])

        lat_min = np.min(lats)
        lat_max = np.max(lats)
        long_min = np.min(longs)
        long_max = np.max(longs)

    max_step = 3000
    max_obstacles = 50
    top = True
    first_pub = 0

    for i, publication in enumerate(full_run_json[:max_step]):
        if plot:
            max_obstacles = max_obstacles if max_obstacles < len(publication["obstacles"]
                                                                 ) else len(publication["obstacles"]
                                                                            )
            obsts = publication["obstacles"][:max_obstacles]
            Obsts = []
            for obst in obsts:
                Obsts.append(mo.obstacle_object_from_mqtt_payload_obstacle_as_dict(obst))

            visualize_obstacles.plot_obstacles(Obsts,
                                               i,
                                               lat_extremes=[lat_min, lat_max],
                                               long_extremes=[long_min, long_max],
                                               )
        else:
            time.sleep(0.3)

        # mqtt_turmu.publish_obstacles(client, topic, Obsts)
        if top:
            publication["obstacles"] = publication["obstacles"][:max_obstacles]
        else:
            publication["obstacles"] = publication["obstacles"][-max_obstacles:]

        client.publish(topic, json.dumps(publication))
        print(f"Publication: {i+1}/{max_step}.")

        # for performance test
        if i == 0:
            first_pub = datetime.datetime.now().strftime('%S,%f')
            pd.DataFrame([first_pub]).to_clipboard(index=False, sep=None, header=None)
            print(f"First publication time in seconds: {first_pub}. Copied to clipboard.")



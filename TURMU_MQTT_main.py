import time

import map_obstacle as mo
import mqtt_turmu

if __name__ == "__main__":

    # Setup local/live mode
    local_mode = False
    input_dir = None  # currently takes csv with lines as objects

    # Setup variables
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()


    # set up topic name here
    # for testing use "testtopic/matyas"
    topic = "testtopic/matyas"

    # connect the client
    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path,
                                     )
    time.sleep(1)

    # Init state variable
    state: str

    # if no actual data import is available, simulate some objects
    if local_mode:
        default_obstacles = mo.generate_default_obstacles_list(number_of_obstacles=3,
                                                               types=["other"],
                                                               )

        actual_map = mo.Map(mapped_obstacles=default_obstacles,
                            obs_threshold_for_new_obstacle_addition=5,
                            )

        candidate_map = mo.Map(mapped_obstacles=[],
                               obs_threshold_for_new_obstacle_addition=0,
                               )    # TODO does this work?

        state = "idle"

    else:
        state = "init"

    # Initialize parameters
    obstacles = []
    prev_len_obstacles = 0
    candidate_obstacles = []
    prev_len_candidate_obstacles = 0
    timestamps = {}



    # Main loop
    while True:
        """
        Possible states are:
        idle
        update_map
        publish_map
        exit
        """

        # init state
        if state == "init":
            while True:
                client.loop(1)
                mqtt_turmu.subscribe(client=client, topic=topic, obstacles=obstacles)

                # check if new items are not added and initial obstacle list is not empty
                if len(obstacles) == prev_len_obstacles and len(obstacles) != 0:
                    state = "idle"
                    actual_map = mo.Map(mapped_obstacles=obstacles[:-1],
                                        obs_threshold_for_new_obstacle_addition=5,
                                        )
                    candidate_obstacles = obstacles[-1]
                    prev_len_candidate_obstacles = 1
                    break
                prev_len_obstacles = len(obstacles)

        if state == "idle":
            while True:
                client.loop(1)
                mqtt_turmu.subscribe(client=client, topic=topic, obstacles=candidate_obstacles)

                if len(candidate_obstacles) == prev_len_candidate_obstacles and len(candidate_obstacles) != 0:
                    state = "update_map"
                    # TODO add these to the candidate map

                    break

                prev_len_candidate_obstacles = len(candidate_obstacles)

    # TODO candidates_map = mo.Map(mapped_objects=None)


    # new_object_found, new_object_idx, paired_mapped_object_idx, paired_new_object_idx = \
    #     mo.find_new_objects(current_map, new_observation)
    #
    # if new_object_found:
    #     current_map.add_new_obstacle(new_object_idx, new_observation)
    #
    #     # TODO
    #     """
    #     Candidates map logic:
    #
    #     1.  Compare the newly observed objects left out from the current_map (i.e. - the ones that don't meet the
    #         threshold criteria or just not the best match) with objects in this map and do the same addition as with the
    #         current map for this map instance.
    #         Set the observation threshold for this map lower (0 is the default).
    #
    #     2.  For those observations in the candidates_map, which reach a higher observation count, move them from the
    #         candidates map to the current map.
    #
    #     """
    #     pass
    # else:
    #     current_map.update_map(paired_mapped_object_idx, paired_new_object_idx, new_observation)

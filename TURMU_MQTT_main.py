import time

import map_obstacle as mo
import mqtt_turmu

if __name__ == "__main__":

    # Setup local/live mode
    local_mode = False
    input_dir = None  # currently takes csv with lines as obstacles

    # Setup variables
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    # set up topic names here
    # for testing use "testtopic/matyas" to listen to
    topic_listen = "testtopic/matyas"

    # for testing use "testtopic/planner"
    topic_publish = "testtopic/planner"

    # for testing use "testtopic/egovehicle"
    topic_egovehicle = "testtopic/egovehicle"

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

    time.sleep(0.1)

    # Init state selector
    state = "init"

    # Initialize parameters
    obstacles = []
    prev_len_obstacles = 0
    new_observation = []
    prev_len_candidate_obstacles = 0

    # parameter of sensor
    observable_area_radius = 50

    # Map initialization and mapping threshold
    map_init_observations = 10
    mapping_threshold = 5
    actual_map = mo.Map()
    candidate_map = mo.Map()

    # Ego vechicle initialization
    ego_vehicle = None

    # debug
    mama: int = 0
    print("start main loop")

    # Main loop
    while True:
        mama += 1
        print(f"iteration {mama}, state: {state}")
        print(f"Actual map objects: {len(actual_map.mapped_obstacles)}")
        print(f"Candidate map objects: {len(candidate_map.mapped_obstacles)}")
        obs_s = []
        for obst in candidate_map.mapped_obstacles:
            obs_s.append(obst.number_of_observations)
        if len(obs_s) != 0:
            print(f"Maximum number of candidate observations: {max(obs_s)}")
        print()

        """
        Possible states are:
        idle
        update_map
        publish_map
        exit
        """
        # init state: set up initial actual map and empty candidate map
        if state == "init":
            # initialize ego vehicle
            ego_vehicle = mo.Egovehicle()

            while True:
                # initialize empty candidate map
                candidate_map = mo.Map(mapped_obstacles=[],
                                       observ_threshold_for_new_obstacle_addition=0
                                       )

                # if no mqtt data import is available, simulate some obstacles
                if local_mode:
                    default_obstacles = mo.generate_default_obstacles_list(number_of_obstacles=3,
                                                                           types=["other"],
                                                                           number_of_observations=map_init_observations,
                                                                           )

                    actual_map = mo.Map(mapped_obstacles=default_obstacles,
                                        observ_threshold_for_new_obstacle_addition=mapping_threshold,
                                        )

                    state = "idle"

                    break

                # if mqtt data import is available, start listening
                else:

                    # listen to MQTT
                    client.loop(0)
                    mqtt_turmu.subscribe(client=client,
                                         topic=topic_listen,
                                         obstacles=obstacles
                                         )

                    # check if new items are not added and initial obstacle list is not empty
                    if len(obstacles) == prev_len_obstacles and len(obstacles) != 0:
                        for obstacle in obstacles:
                            obstacle.number_of_observations = map_init_observations
                        actual_map = mo.Map(mapped_obstacles=obstacles,
                                            observ_threshold_for_new_obstacle_addition=5,
                                            )

                        while len(ego_vehicle.timestamps) == 0:
                            client.loop(0)
                            mqtt_turmu.subscribe(client=client,
                                                 topic=topic_egovehicle,
                                                 timestamps=ego_vehicle.timestamps,
                                                 sensor_locations=ego_vehicle.sensor_locations,
                                                 )

                        # go to idle mode
                        state = "idle"
                        break

                    else:
                        state = "init"

                    # update input counter
                    prev_len_obstacles = len(obstacles)

        # idle state: listen to the MQTT topic, and obtain new broadcast observation (i.e., obstacles)
        elif state == "idle":
            while True:
                # if no mqtt data import is available, generate obstacles similar to the ones in the map
                if local_mode:
                    time.sleep(5)
                    new_observation = mo.generate_default_obstacles_list(like=actual_map.mapped_obstacles)
                    sensor_location = [0, 0]

                    state = "update_map"
                    break

                else:
                    # listen to MQTT inputs
                    client.loop(0)
                    mqtt_turmu.subscribe(client=client,
                                         topic=topic_listen,
                                         obstacles=new_observation)

                if len(new_observation) == prev_len_candidate_obstacles and len(new_observation) != 0:
                    # go to map updating mode
                    state = "update_map"
                    while len(ego_vehicle.timestamps) == 0:
                        client.loop(0)
                        mqtt_turmu.subscribe(client=client,
                                             topic=topic_egovehicle,
                                             timestamps=ego_vehicle.timestamps,
                                             sensor_locations=ego_vehicle.sensor_locations,
                                             )

                    break

                # update input obstacles counter
                prev_len_candidate_obstacles = len(new_observation)

        # update_map state: include obstacles in candidate map, and if they cross the threshold,
        #                   include them in the actual map, too
        elif state == "update_map":
            print(f"Number of new observations before actual map update: {len(new_observation)}")
            # subset of maps that can be observed
            actual_map_observed = actual_map.subset_in_observed_area(
                sensor_location=ego_vehicle.sensor_locations[-1],
                observable_area_radius=observable_area_radius,
            )
            candidate_map_observed = candidate_map.subset_in_observed_area(
                sensor_location=ego_vehicle.sensor_locations[-1],
                observable_area_radius=observable_area_radius,
            )

            # find pairings for actual map
            paired_actual_mapped_obstacle_indices, paired_new_obstacle_indices = mo.pair_obstacles(
                current_map=actual_map_observed,
                newly_observed_obstacles=new_observation,
            )

            # update paired mapped obstacles
            actual_map.update_map(
                paired_mapped_obstacles_indices=paired_actual_mapped_obstacle_indices,
                paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                newly_observed_obstacles=new_observation,
            )

            # remove paired obstacles from the list of new observation
            paired_new_obstacle_indices.sort()
            for i, index in enumerate(paired_new_obstacle_indices):
                new_observation.pop(index - i)

            print(f"Number of new observations before candidate map update: {len(new_observation)}")
            # if there's anything remaining in new_observations not paired up with the actual map
            if len(new_observation) != 0:

                # find pairings for candidate map
                paired_candidate_mapped_obstacle_indices, paired_new_obstacle_indices = mo.pair_obstacles(
                    current_map=candidate_map_observed,
                    newly_observed_obstacles=new_observation,
                )

                # update paired candidate obstacles
                candidate_map.update_map(
                    paired_mapped_obstacles_indices=paired_candidate_mapped_obstacle_indices,
                    paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                    newly_observed_obstacles=new_observation,
                )

                # remove paired obstacles from the list of new observation
                paired_new_obstacle_indices.sort()
                for i, index in enumerate(paired_new_obstacle_indices):
                    new_observation.pop(index - i)

            print(f"Number of new observations after candidate map update: {len(new_observation)}")
            # add anything that remains to the candidate map
            if len(new_observation) != 0:
                for new_obstacle in new_observation:

                    # set unique obstacle_id
                    new_obstacle.obstacle_id = max([actual_map.highest_id(), candidate_map.highest_id()]) + 1

                    # add to candidate map
                    candidate_map.mapped_obstacles.append(new_obstacle)

                # empty new_observation array
                new_observation = []
            print("reached end of map update")
            print()
            # for state selector choice
            actual_obstacles_before_update = len(actual_map.mapped_obstacles)

            # TODO decrement counter for obstacles that should be observed but are not

            # include those obstacles from the candidate map, which have reached the threshold, to the actual map
            mo.add_obstacles_above_threshold(
                candidate_map=candidate_map,
                actual_map=actual_map,
            )

            # set next state - publish obstacles, if new obstacle has been added to actual_map
            #                  idle, if actual map hasn't changed
            if actual_obstacles_before_update != len(actual_map.mapped_obstacles):
                state = "publish_map"
            else:
                state = "idle"

        # publish map state: publish map through mqtt
        elif state == "publish_map":
            print("publish map reached")
            for obstacle_to_publish in actual_map.mapped_obstacles:
                mqtt_turmu.publish_obstacle(client=client,
                                            topic=topic_publish,
                                            obstacle=obstacle_to_publish,
                                            )

            # set next state
            state = "idle"

        # exit state: exit the program
        # state currently unused
        elif state == "exit":
            pass

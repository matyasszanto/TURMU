import datetime
import time

import map_obstacle as mo
import mqtt_turmu

if __name__ == "__main__":

    # Setup variables
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()

    # set up topic names here
    # for testing use "testtopic/matyas" to listen to
    # topic_listen = "iotac/Twizy-1/obstacles"
    topic_listen = "iotac/VirtualVehicle-1/obstacles"

    # for testing use "testtopic/planner"
    topic_publish = "iotac/planner"

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
    new_observation = []

    # parameter of sensor
    observable_area_radius = 50

    # Map initialization and mapping threshold
    map_init_observations = 1
    mapping_promotion_threshold = 5
    penalty_points_for_demotion = 3
    actual_map = mo.Map()
    candidate_map = mo.Map()

    # map publication threshold
    publish_timeout = 5     # seconds

    # Ego-vehicle initialization
    ego_vehicle = None

    # debug
    loop_count: int = 0
    print("start main loop")

    last_publish_time = datetime.datetime.now()

    # Main loop
    while True:
        loop_count += 1
        print(f"iteration {loop_count}, state: {state}")
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

            # initialize empty candidate map
            candidate_map = mo.Map(obstacles_to_map=[],
                                   promotion_threshold=0,
                                   )
            # listen to MQTT
            while len(obstacles) == 0:
                client.loop(0.1)
                mqtt_turmu.subscribe(client=client,
                                     topic=topic_listen,
                                     obstacles=obstacles,
                                     sensor_locations=ego_vehicle.sensor_locations,
                                     timestamps=ego_vehicle.timestamps,
                                     )

            # initialize actual map
            for obstacle in obstacles:
                obstacle.number_of_observations = map_init_observations
            actual_map = mo.Map(obstacles_to_map=obstacles, promotion_threshold=mapping_promotion_threshold)

            state = "idle"

            last_publish_time = datetime.datetime.now()
            continue

        # idle state: listen to the MQTT topic, and obtain new broadcast observation (i.e., obstacles)
        #             and sensor locations as well as separate timestamps to the ego_vehicle instant
        elif state == "idle":
            # listen to MQTT
            while len(new_observation) == 0:
                client.loop(1)
                mqtt_turmu.subscribe(client=client,
                                     topic=topic_listen,
                                     obstacles=new_observation,
                                     sensor_locations=ego_vehicle.sensor_locations,
                                     timestamps=ego_vehicle.timestamps,
                                     )
                since_last_publish = datetime.datetime.now() - last_publish_time
                if since_last_publish.seconds > publish_timeout:
                    print("publish timout")
                    state = "publish_map"
                    break
            if state != "publish_map":
                state = "update_map"

            continue
        # update_map state: include obstacles in candidate map, and if they cross the threshold,
        #                   include them in the actual map, too
        elif state == "update_map":
            # for state selector choice
            actual_obstacles_before_update = len(actual_map.mapped_obstacles)

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
                threshold=1.0,
            )

            # update paired mapped obstacles
            actual_map.update_map(paired_mapped_obstacles_indices=paired_actual_mapped_obstacle_indices,
                                  paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                                  newly_observed_obstacles=new_observation,
                                  )

            # penalize not observed obstacles and demote them if necessary
            mo.demote_obstacle(actual_map_observable_subset=actual_map_observed, actual_map=actual_map,
                               paired_mapped_obstacles=paired_actual_mapped_obstacle_indices,
                               candidate_map=candidate_map, candidate_map_observable_subset=candidate_map_observed,
                               penalty_points_for_demotion=penalty_points_for_demotion,
                               )

            # remove paired obstacles from the list of new observation
            paired_new_obstacle_indices.sort()
            for i, index in enumerate(paired_new_obstacle_indices):
                new_observation.pop(index - i)

            # if there's anything remaining in new_observations not paired up with the actual map
            if len(new_observation) != 0:

                # find pairings for candidate map
                paired_candidate_mapped_obstacle_indices, paired_new_obstacle_indices = mo.pair_obstacles(
                    current_map=candidate_map_observed,
                    newly_observed_obstacles=new_observation,
                    threshold=0.8,
                )

                # update paired candidate obstacles
                candidate_map.update_map(paired_mapped_obstacles_indices=paired_candidate_mapped_obstacle_indices,
                                         paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                                         newly_observed_obstacles=new_observation,
                                         )

                # remove paired obstacles from the list of new observation
                paired_new_obstacle_indices.sort()
                for i, index in enumerate(paired_new_obstacle_indices):
                    new_observation.pop(index - i)

            # add anything that remains to the candidate map
            if len(new_observation) != 0:
                for new_obstacle in new_observation:

                    # set unique obstacle_id
                    new_obstacle.obstacle_id = max([actual_map.highest_id(), candidate_map.highest_id()]) + 1
                    print(f"new ID is: {new_obstacle.obstacle_id}")

                    # add to candidate map
                    candidate_map.mapped_obstacles.append(new_obstacle)

                # empty new_observation array
                new_observation = []

            # include those obstacles from the candidate map, which have reached the threshold, to the actual map
            mo.promote_obstacles(candidate_map=candidate_map, actual_map=actual_map)

            # set next state - publish obstacles, if new obstacle has been added to actual_map
            #                  idle, if actual map hasn't changed
            if actual_obstacles_before_update != len(actual_map.mapped_obstacles):
                state = "publish_map"
            else:
                state = "idle"
            continue
        # publish map state: publish map through mqtt
        elif state == "publish_map":
            # publish mapped objects
            actual_map.publish_map(client=client, topic=topic_publish)

            # restart timer for publish timeout
            last_publish_time = datetime.datetime.now()

            # set next state
            state = "idle"
            continue
        # exit state: exit the program
        # state currently unused
        elif state == "exit":
            pass

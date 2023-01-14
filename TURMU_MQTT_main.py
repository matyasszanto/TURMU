import datetime
import time

import numpy as np

import map_obstacle as mo
import mqtt_turmu

from matplotlib import cm

if __name__ == "__main__":

    # Set up variables
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
    # topic_egovehicle = "testtopic/egovehicle"

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

    # wait for connection to finish
    time.sleep(0.1)

    # Init state selector
    state = "init"

    # Initialize parameters
    obstacles = []
    new_observation = []

    # parameter of sensor
    observable_area_radius = 0.0002   # 0.00012

    # Map initialization and mapping threshold
    map_init_observations = 30
    mapping_promotion_obs_threshold = 8
    penalty_points_for_demotion = 20
    employed_map = mo.Map()
    candidate_map = mo.Map()

    # similarity thresholds - higher value means more strict pairing rules
    employed_map_similarity_threshold = 0.999
    candidate_map_similarity_threshold = 0.9
    mapping_promotion_similarity_threshold = 0.92

    # map publication threshold
    publish_timeout = 50     # seconds TODO this was changed from 5 for performance test

    # Ego-vehicle initialization
    ego_vehicle = None

    # map visualization
    plots_dir = f"plots/{datetime.datetime.now()}"
    sim_num_obsts = 80
    colors = cm.tab20c(np.linspace(0, 1, sim_num_obsts + 10))  # gist_rainbow    viridis    tab20 tab20b tab20c

    # performance test
    published_positions = []

    # debug
    verbose = True
    plot = False
    loop_count: int = 0
    print("start main loop")

    last_publish_time = datetime.datetime.now()

    # Main loop
    while True:
        loop_count += 1
        if verbose:
            print(f"iteration {loop_count}, state: {state}")
            print(f"Employed map objects: {len(employed_map.mapped_obstacles)}")
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

        try:
            # init state: set up initial employed map and empty candidate map
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
                # initialize employed map
                for obstacle in obstacles:
                    obstacle.number_of_observations = map_init_observations

                employed_map = mo.Map(obstacles_to_map=[],
                                      promotion_threshold=mapping_promotion_obs_threshold,
                                      )
                if plot:
                    employed_map.visualize_map(index=loop_count,
                                               colors=colors,
                                               out_dir=plots_dir,
                                               egovehicle=ego_vehicle,
                                               observable_radius=observable_area_radius,
                                               )

                state = "idle"

                last_publish_time = datetime.datetime.now()
                continue

            # idle state: listen to the MQTT topic, and obtain new broadcast observation (i.e., obstacles)
            #             and sensor locations as well as separate timestamps to the ego_vehicle instance
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
                        print("publish timeout")
                        state = "publish_map"
                        break
                if state != "publish_map":
                    state = "update_map"

                continue
            # update_map state: include obstacles in candidate map, and if they cross the threshold,
            #                   include them in the employed map, too
            elif state == "update_map":

                if plot:
                    new_observation_map = mo.Map(obstacles_to_map=new_observation)

                    new_observation_map.visualize_map(index=loop_count,
                                                      out_dir=plots_dir+"/no",
                                                      colors=colors,
                                                      egovehicle=ego_vehicle,
                                                      observable_radius=observable_area_radius,
                                                      )

                # for state selector choice
                employed_obstacles_before_update = len(employed_map.mapped_obstacles)

                # subset of maps that can be observed
                employed_map_observed = employed_map.subset_in_observed_area(
                    sensor_location=ego_vehicle.sensor_locations[-1],
                    observable_area_radius=observable_area_radius,
                )
                candidate_map_observed = candidate_map.subset_in_observed_area(
                    sensor_location=ego_vehicle.sensor_locations[-1],
                    observable_area_radius=observable_area_radius*10,
                )

                # find pairings for employed map
                paired_employed_mapped_obstacle_indices, paired_new_obstacle_indices = mo.pair_obstacles(
                    current_map=employed_map_observed,
                    newly_observed_obstacles=new_observation,
                    threshold=employed_map_similarity_threshold,
                )

                # update paired mapped obstacles
                employed_map_observed.update_map(paired_mapped_obstacles_indices=paired_employed_mapped_obstacle_indices,
                                                 paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                                                 newly_observed_obstacles=new_observation,
                                                 )

                # penalize not observed obstacles and demote them if necessary
                mo.demote_obstacle(employed_map_observable_subset=employed_map_observed,
                                   employed_map=employed_map,
                                   paired_mapped_obstacles=paired_employed_mapped_obstacle_indices,
                                   candidate_map=candidate_map,
                                   candidate_map_observable_subset=candidate_map_observed,
                                   penalty_points_for_demotion=penalty_points_for_demotion,
                                   )

                # remove paired obstacles from the list of new observation
                paired_new_obstacle_indices.sort()
                for i, index in enumerate(paired_new_obstacle_indices):
                    new_observation.pop(index - i)

                # if there's anything remaining in new_observations not paired up with the employed map
                if len(new_observation) != 0:

                    # find pairings for candidate map
                    paired_candidate_mapped_obstacle_indices, paired_new_obstacle_indices = mo.pair_obstacles(
                        current_map=candidate_map_observed,
                        newly_observed_obstacles=new_observation,
                        threshold=candidate_map_similarity_threshold,
                    )

                    # update paired candidate obstacles
                    candidate_map_observed.update_map(
                        paired_mapped_obstacles_indices=paired_candidate_mapped_obstacle_indices,
                        paired_newly_observed_obstacle_indices=paired_new_obstacle_indices,
                        newly_observed_obstacles=new_observation)

                    # remove paired obstacles from the list of new observation
                    paired_new_obstacle_indices.sort()
                    for i, index in enumerate(paired_new_obstacle_indices):
                        new_observation.pop(index - i)

                # add anything that remains to the candidate map
                if len(new_observation) != 0:
                    for new_obstacle in new_observation:

                        # set unique obstacle_id
                        new_obstacle.obstacle_id = max([employed_map.highest_id(), candidate_map.highest_id()]) + 1
                        if verbose:
                            print(f"new ID is: {new_obstacle.obstacle_id}")

                        # add to candidate map
                        candidate_map.mapped_obstacles.append(new_obstacle)
                    if verbose:
                        print()
                    # empty new_observation array
                    new_observation = []

                # include those obstacles from the candidate map, which have reached the threshold, to the employed map
                mo.promote_obstacles(candidate_map=candidate_map,
                                     employed_map=employed_map,
                                     promotion_merge_threshold=mapping_promotion_similarity_threshold,
                                     )

                # set next state - publish obstacles, if new obstacle has been added to employed_map
                #                  idle, if employed map hasn't changed
                if employed_obstacles_before_update != len(employed_map.mapped_obstacles):
                    state = "publish_map"
                else:
                    state = "idle"

                if plot:
                    employed_map.visualize_map(index=loop_count,
                                               out_dir=plots_dir,
                                               colors=colors,
                                               egovehicle=ego_vehicle,
                                               observable_radius=observable_area_radius,
                                               )

                    candidate_map.visualize_map(index=loop_count,
                                                out_dir=plots_dir+"/cm",
                                                colors=colors,
                                                egovehicle=ego_vehicle,
                                                observable_radius=observable_area_radius,
                                                )

                continue

            # publish map state: publish map through mqtt
            elif state == "publish_map":
                print(f"Publish start time: {datetime.datetime.now().strftime('%S,%f')}")
                published_positions.append([employed_map.mapped_obstacles[0].lat,
                                            employed_map.mapped_obstacles[0].long]
                                           )
                np.savetxt("positions.csv", np.array(published_positions), delimiter=";")
                # publish mapped objects
                employed_map.publish_map(client=client, topic=topic_publish)

                # restart timer for publish timeout
                last_publish_time = datetime.datetime.now()

                # set next state
                state = "idle"
                continue

        except Exception as e:
            print(f"Error: {e}")
            print(f"Final index: {loop_count}")
            print(f"Final state: {state}")
            print("Continuing...")
            pass

import map_object as mo
import mqtt_turmu

if __name__ == "__main__":

    # Setup local/live mode
    input_available = False  # set to True if file with objects is available
    input_dir = None  # currently takes csv with lines as objects

    # Setup variables
    # parameters for Tecnalia MQTT broker
    broker, port, client_id, username, password, ca_certs_path, certfile_path, keyfile_path = \
        mqtt_turmu.load_default_params()


    # set up topic name here
    # for testing use "testtopic/matyas"
    topic = "testtopic/matyas"

    # TODO logic for MQTT live update
    client = mqtt_turmu.connect_mqtt(broker,
                                     port,
                                     client_id,
                                     username,
                                     password,
                                     ca_certs_path,
                                     certfile_path,
                                     keyfile_path,
                                     )

    # for testing
    if not input_available:
        mo.turmu_offline_mode_publish(3, client)
        pass

    client.loop_start()

    mqtt_turmu.subscribe(client, topic, current_full_map=None, candidate_map=None)

    current_map = mo.Map(mapped_objects=objects_list,
                         obs_threshold_for_new_object_addition=1,
                         )
    # TODO candidates_map = mo.Map(mapped_objects=None)


    new_object_found, new_object_idx, paired_mapped_object_idx, paired_new_object_idx = \
        mo.find_new_objects(current_map, new_observation)

    if new_object_found:
        current_map.add_new_object(new_object_idx, new_observation)

        # TODO
        """
        Candidates map logic:
        
        1.  Compare the newly observed objects left out from the current_map (i.e. - the ones that don't meet the
            threshold criteria or just not the best match) with objects in this map and do the same addition as with the
            current map for this map instance.
            Set the observation threshold for this map lower (0 is the default).
            
        2.  For those observations in the candidates_map, which reach a higher observation count, move them from the
            candidates map to the current map. 
        
        """
        pass
    else:
        current_map.update_map(paired_mapped_object_idx,
                               paired_new_object_idx,
                               new_observation,
                               )

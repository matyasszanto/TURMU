import map_obstacle as mo

if __name__ == "__main__":

    # Setup local/live mode

    input_available = False  # set to True if file with objects is available
    input_dir = None  # currently takes csv with lines as objects

    # Setup variables

    # Load map objects
    if input_available:
        obstacles_list = mo.read_obstacles_from_input(input_dir)

    else:
        obstacles_list = mo.generate_default_obstacles_list()

    for item in obstacles_list:
        item.print()

    current_map = mo.Map(mapped_obstacles=obstacles_list, observ_threshold_for_new_obstacle_addition=1)

    new_observation = mo.generate_default_obstacles_list(number_of_obstacles=3)

    new_obstacle_found, new_obstacle_idx, paired_mapped_obstacle_idx, paired_new_obstacle_idx = \
        mo.find_new_obstacles(current_map,
                              new_observation
                              )

    if new_obstacle_found:
        current_map.add_new_obstacle(new_obstacle_idx,
                                     new_observation
                                     )

        """
        Candidates map logic:
        
        1.  Compare the newly observed obstacles left out from the current_map (i.e. - the ones that don't meet the
            threshold criteria or just not the best match) with obstacles in this map and do the same addition as with
            the current map for this map instance.
            Set the observation threshold for this map lower (0 is the default).
            
        2.  For those obstacles in the candidates_map, which reach a higher observation count, move them from the
            candidates map to the current map. 
        
        """
        pass
    else:
        current_map.update_map(paired_mapped_obstacle_idx,
                               paired_new_obstacle_idx,
                               new_observation)

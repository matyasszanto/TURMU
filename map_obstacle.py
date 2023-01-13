import datetime
import os

import numpy as np
import math
from scipy.optimize import linear_sum_assignment as magyar
import json
import copy

import mqtt_turmu
import visualize_obstacles as vo

# set up sigma parameters for rbf calculation
# higher sigma means more tolerance
sigmas = [0.00001,  # sigma_latitude
          0.00001,  # sigma_longitude
          0.000001,  # sigma_speed
          1,  # sigma_width
          1,  # sigma_length
          ]


class Obstacle:
    def __init__(self,
                 obstacle_id=0,
                 obstacle_type="empty",
                 lat=0.0,
                 long=0.0,
                 speed=0.0,
                 width=0.0,
                 length=0.0,
                 number_of_observations=1,
                 first_timestamp=None,
                 latest_timestamp=None,
                 ):
        """
        Obstacle class

        :param obstacle_id: ID number of obstacle
        :param obstacle_type: type of obstacle: 0 - empty, 1 - obstacle, 2- vehicle, 3 - pedestrian
        :param lat: lateral coordinates of obstacle
        :param long: longitudinal coordinates of obstacle
        :param speed: speed of obstacle
        :param width: width of obstacle
        :param length: length of obstacle
        :param number_of_observations: number of times obstacle has already been observed
        :param first_timestamp: timestamp of when obstacle was first received
        :param latest_timestamp: timestamp of when obstacle was last seen
        """

        # parameters
        self.obstacle_id = obstacle_id
        self.obstacle_type = obstacle_type  # ["empty", "obstacle", "vehicle", "pedestrian"]
        self.lat = lat
        self.long = long
        self.speed = speed
        self.width = width
        self.length = length
        self.number_of_observations = number_of_observations
        self.first_timestamp = first_timestamp
        self.latest_timestamp = latest_timestamp
        self.penalty_points: int = 0

    def print(self):
        """
        print parameters of Obstacle instance
        """
        print(f"Obstacle id:        {self.obstacle_id}")
        print(f"Obstacle type:      {self.obstacle_type}")
        print(f"Lateral:            {self.lat}")
        print(f"Longitudinal:       {self.long}")
        print(f"Speed:              {self.speed}")
        print(f"Width:              {self.width}")
        print(f"Length:             {self.length}")
        print(f"Observations:       {self.number_of_observations}")
        print(f"First observation:  {self.first_timestamp}")
        print(f"Latest observation: {self.latest_timestamp}")
        print()

    def strip_params(self):
        """
        Strips the Obstacle instance from its non-numeric parameters (e.g., its ID and its type)

        :return: numpy array of lat, long, speed, width, length
        """
        obstacle_without_id_and_type = np.array([self.lat,
                                                 self.long,
                                                 self.speed,
                                                 self.width,
                                                 self.length,
                                                 ]
                                                )
        return obstacle_without_id_and_type

    def as_dict(self):
        """
        creates a dictionary from the class parameters

        :return: {"obstacleId": obstacle_id,"type": obstacle_type, "latitude": lat, "longitude": long,
                  "speed": speed, "width": width, "length": length, "observations": no. of observations
                  "timestamp": latest_timestamp}
        """

        # check if timestamp yields string or datetime.datetime
        if isinstance(self.latest_timestamp, str):
            timestamp_in_dict = self.latest_timestamp
        else:
            # timestamp_in_dict = self.latest_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            timestamp_in_dict = self.latest_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        return {"obstacleId": self.obstacle_id,
                "type": self.obstacle_type,
                "latitude": self.lat,
                "longitude": self.long,
                "speed": self.speed,
                "width": self.width,
                "length": self.length,
                "observations": self.number_of_observations,
                "timestamp": timestamp_in_dict
                }

    def as_json(self):
        obstacle_json = json.dumps(self.as_dict(), indent=4, default=str)
        return obstacle_json


"""
def write_obstacle_to_output(obstacle: Obstacle):
    "
    method to write new obstacles to MQTT or output

    :param obstacle: Obstacle instance to write
    "
    # TODO write_obstacle_to_output method - if necessary?

    pass
"""


def generate_default_obstacles_list(number_of_obstacles=3,
                                    types=None,
                                    number_of_observations=1,
                                    like: [Obstacle] = None,
                                    uniform=False,
                                    ):
    """
    Generates a list of Obstacle instances of length number_of_obstacles with random numeric parameters for
    long and lat, and with fixed values for types

    :param uniform: to generate identical obstacles
    :param number_of_obstacles: number of obstacles to be generated
                                if "like" is not None, this parameter is not used.
    :param types: list of types from ["empty", "obstacle", "vehicle", "pedestrian"]
                  if "like" is not None, this parameter is not used.
    :param number_of_observations: number of observations parameter of generated obstacles
                                   if "like" is not None, this parameter is not used.
    :param like: list of obstacles that the generated obstacles should resemble
    :return: ndarray of Obstacle instances with number of observations set to 5 to show them on the map
    """

    # get current time as formatted string
    # current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    number_of_obstacles = number_of_obstacles if like is None else len(like)

    # obstacle list to be generated
    list_of_obstacles = np.empty(number_of_obstacles, dtype=Obstacle)

    if like is None:
        # check types var
        if not isinstance(types, list) and not isinstance(types[0], str):
            types = ["empty", "obstacle", "vehicle", "pedestrian"]
            # types = ["0", "1", "2", "3"]
        else:
            for type_ in types:
                # if type_ not in ["empty", "obstacle", "vehicle", "pedestrian"]:
                if type_ not in ["0", "1", "2", "3"]:
                    types = ["empty", "obstacle", "vehicle", "pedestrian"]
                    # types = ["0", "1", "2", "3"]
                    break

        obstacle_types = (np.array(types))
        for i in range(number_of_obstacles):
            current_type = np.random.choice(obstacle_types)
            if current_type == "0":     # vehicle
                current_width = 2
                current_length = 3.5
            elif current_type == "1":   # pedestrian
                current_width = 0.4
                current_length = 0.4
            else:
                current_width = 1
                current_length = 1

            if uniform:
                lat = 0
                long = 0
            else:
                lat = np.random.uniform(-15, 15)
                long = np.random.uniform(-5, 5)

            list_of_obstacles[i] = Obstacle(obstacle_id=i,
                                            obstacle_type=current_type,
                                            lat=lat,
                                            long=long,
                                            speed=0,
                                            width=current_width,
                                            length=current_length,
                                            number_of_observations=number_of_observations,
                                            first_timestamp=current_time,
                                            latest_timestamp=current_time,
                                            )

    # if a list of obstacles is given in "like"
    else:
        for i, like_obstacle in enumerate(like):
            list_of_obstacles[i] = Obstacle(obstacle_id=i,
                                            obstacle_type=like_obstacle.obstacle_type,
                                            lat=like_obstacle.lat + np.random.uniform(-5, 5),
                                            long=like_obstacle.long + np.random.uniform(-1, 1),
                                            speed=0,
                                            width=like_obstacle.width,
                                            length=like_obstacle.length,
                                            number_of_observations=1,
                                            first_timestamp=current_time,
                                            latest_timestamp=current_time,
                                            )

    return list_of_obstacles


def obstacle_object_from_mqtt_payload_obstacle_as_dict(obstacle_as_dict=None):
    """
    Creates an obstacle from an MQTT "obstacles" payload
    :param obstacle_as_dict: a singular obstacle from the "obstacles" payload
    :return: Obstacle instance
    """
    if obstacle_as_dict is None:
        obstacle_as_dict = {}
    generated_obstacle = Obstacle(obstacle_id=0,
                                  obstacle_type=obstacle_as_dict["type"],
                                  lat=float(obstacle_as_dict["latitude"]),
                                  long=float(obstacle_as_dict["longitude"]),
                                  speed=float(obstacle_as_dict["speed"]),
                                  width=float(obstacle_as_dict["width"]),
                                  length=float(obstacle_as_dict["length"]),
                                  number_of_observations=1,
                                  latest_timestamp=datetime.datetime.strptime(obstacle_as_dict["timestamp"],
                                                                              # "%Y-%m-%dT%H:%M:%S.%fZ",
                                                                              "%Y-%m-%dT%H:%M:%SZ",
                                                                              ),
                                  first_timestamp=datetime.datetime.strptime(obstacle_as_dict["timestamp"],
                                                                             # "%Y-%m-%dT%H:%M:%S.%fZ",
                                                                             "%Y-%m-%dT%H:%M:%SZ",
                                                                             ),
                                  )
    return generated_obstacle


class Map:
    def __init__(self, obstacles_to_map=None, promotion_threshold=0, subset=False):
        """
        Class for mapped obstacles

        :param obstacles_to_map: List of Obstacle instances to map
        :param promotion_threshold: threshold value, denoting
                                                           how many observations shall a new value be added
        :param subset: Flag to show if only map subset is created at this step - obstacle ids won't be reinitialized
        """
        if obstacles_to_map is None:
            obstacles_to_map = []

        # initialize indexes if necessary
        if not subset:
            for i, obstacle in enumerate(obstacles_to_map):
                obstacle.obstacle_id = i
            # if new map: make a copy of obstacles to be mapped
            self.mapped_obstacles = copy.deepcopy(obstacles_to_map)
        else:
            # if subset: copy items list to map
            self.mapped_obstacles = obstacles_to_map

        self.number_of_mapped_obstacles = len(obstacles_to_map) if self.mapped_obstacles is not None else 0
        self.promotion_threshold = promotion_threshold

    def update_map(self,
                   paired_mapped_obstacles_indices,
                   paired_newly_observed_obstacle_indices,
                   newly_observed_obstacles,
                   promotion=False
                   ):
        """
        Method for updating means and timestamps of mapped obstacles with new observation

        :param paired_mapped_obstacles_indices: output of pair_obstacles function
        :param paired_newly_observed_obstacle_indices: output of pair_obstacles function
        :param newly_observed_obstacles: array of instances of map_obstacle.Obstacle class
        :param promotion: flag to show if update type is promotion
        """

        for i, paired_mapped_index in enumerate(paired_mapped_obstacles_indices):

            # get means and no_observations from paired mapped obstacle
            mapped_means = self.mapped_obstacles[paired_mapped_index].strip_params()
            n = self.mapped_obstacles[paired_mapped_index].number_of_observations

            # get pairing index
            paired_newly_observed_obstacle_index = paired_newly_observed_obstacle_indices[i]

            # get values from newly observed paired obstacle
            new_vals = newly_observed_obstacles[paired_newly_observed_obstacle_index].strip_params()

            new_number_of_observations = \
                newly_observed_obstacles[paired_newly_observed_obstacle_index].number_of_observations

            # calculate new means
            updated_means = np.empty_like(mapped_means)
            for j, (old_val, new_val) in enumerate(zip(mapped_means, new_vals)):
                weighted_mean = old_val * n
                weighted_new_val = new_val * new_number_of_observations
                updated_means[j] = (weighted_mean + weighted_new_val) / (n + new_number_of_observations)

            # update mapped obstacle means in map class
            self.mapped_obstacles[paired_mapped_index].lat = updated_means[0]
            self.mapped_obstacles[paired_mapped_index].long = updated_means[1]
            self.mapped_obstacles[paired_mapped_index].speed = updated_means[2]
            self.mapped_obstacles[paired_mapped_index].width = updated_means[3]
            self.mapped_obstacles[paired_mapped_index].length = updated_means[4]

            # increase number of observations for obstacle
            self.mapped_obstacles[paired_mapped_index].number_of_observations += new_number_of_observations

            # update latest_timestamp of matched object
            self.mapped_obstacles[paired_mapped_index].latest_timestamp = \
                newly_observed_obstacles[paired_newly_observed_obstacle_index].latest_timestamp

        # update number of mapped objects
        self.number_of_mapped_obstacles = len(self.mapped_obstacles)

    def subset_in_observed_area(self, sensor_location=None, observable_area_radius=50):
        """
        Function to return the subset of obstacles that are in the area observable by the sensor
        at the time of measurement

        :param sensor_location: current location (latitude and longitude) of the Lidar
        :param observable_area_radius: constant that describes the size of the radius of the observable area
        :return: 2 values:
                    1. the observable part of the map as a map_obstacle.Map
                    2. a lookup table between the obstacle indices of the input map and its observable subset
        """
        if sensor_location is None:
            sensor_location = [0, 0]

        obstacles_subset = []

        for i, obstacle in enumerate(self.mapped_obstacles):
            # calculate distance from sensor location
            distance = 0
            for p1, p2 in zip(sensor_location, [obstacle.lat, obstacle.long]):
                distance += (p2 - p1)**2
            distance = math.sqrt(distance)
            if distance < observable_area_radius:
                obstacles_subset.append(obstacle)

        map_subset = Map(obstacles_to_map=obstacles_subset,
                         promotion_threshold=self.promotion_threshold, subset=True)

        return map_subset

    def highest_id(self):
        """
        finds the highest id of the obstacles contained in the map

        :return: highest id
        """
        ids = []
        for obstacle in self.mapped_obstacles:
            ids.append(obstacle.obstacle_id)

        highest_id = 0 if len(ids) == 0 else max(ids)

        return highest_id

    def publish_map(self, client, topic):
        """
        publishes the obstacles mapped in the object to the given topic
        :param client: MQTT client
        :param topic: topic to publish on
        """

        mqtt_turmu.publish_obstacles(client=client,
                                     topic=topic,
                                     obstacles=self.mapped_obstacles,
                                     )

    def visualize_map(self, index, out_dir, colors=None, egovehicle=None, observable_radius=0):
        """
        method for visualizing mapped obstacles
        :param index: loop index for output plot (.png) naming
        :param out_dir: directory to save output to
        :param colors: pre-defined colors array
        :param egovehicle: ego vehicle object for plotting ego location
        :param observable_radius: radius used for creating map subsets
        """
        # create directory
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        # colors should not be None, but just in case
        if colors is None:
            colors = []

        # check if map is empty
        if len(self.mapped_obstacles) != 0:

            # for live calculated min-max values
            # currently unused
            lats = np.array(list(o.lat for o in self.mapped_obstacles))
            longs = np.array(list(o.long for o in self.mapped_obstacles))
            lat_min = np.min(lats)
            lat_max = np.max(lats)
            long_min = np.min(longs)
            long_max = np.max(longs)

            # run plotting function
            vo.plot_obstacles(obstacles_list=self.mapped_obstacles,
                              index=index,
                              # long_extremes=[long_min, long_max],     # use this for live calculated values
                              # lat_extremes=[lat_min, lat_max],        # use this for live calculated values
                              long_extremes=[-2.87161, -2.87119],       # use this for real_test.json
                              lat_extremes=[43.29708, 43.29746],        # use this for real_test.json
                              path=out_dir,
                              colors=colors,
                              ego_pos=egovehicle.sensor_locations[-1],
                              observable_radius=observable_radius,
                              )


def demote_obstacle(employed_map_observable_subset: Map,
                    employed_map: Map,
                    paired_mapped_obstacles: list,
                    candidate_map: Map,
                    candidate_map_observable_subset: Map,
                    penalty_points_for_demotion: int,
                    ):

    """
    Demote obstacles that have not been observed for the last "number of missed observations to demote" times.

    :param employed_map_observable_subset: Map object of currently observed employed map
    :param employed_map: Map object of employed map
    :param paired_mapped_obstacles: Output vector of indices of magyar algorithm
    :param candidate_map: Map object of candidate map
    :param candidate_map_observable_subset: Map object of currently observed candidate map
    :param penalty_points_for_demotion: Threshold value for obstacle demotion
    """
    # find obstacles that should have been observed
    should_be_observed = np.array(employed_map_observable_subset.mapped_obstacles)

    # find obstacles that were actually observed
    are_observed = np.array(employed_map_observable_subset.mapped_obstacles)[paired_mapped_obstacles]

    # find missing elements
    mask = np.isin(should_be_observed, are_observed)

    # iterate through missing elements
    for not_observed_obstacle in should_be_observed[~mask]:

        # increment times missed
        not_observed_obstacle.penalty_points += 1

        # demote to candidate map, if times missed is above threshold
        if not_observed_obstacle.penalty_points > penalty_points_for_demotion:
            # reset number of observation below map addition threshold
            not_observed_obstacle.number_of_observations = employed_map.promotion_threshold - 1

            # remove obstacle from employed map and its observed version
            employed_map.mapped_obstacles.remove(not_observed_obstacle)
            employed_map_observable_subset.mapped_obstacles.remove(not_observed_obstacle)

            # add obstacle to candidate map and its observed version
            candidate_map.mapped_obstacles.append(not_observed_obstacle)
            candidate_map_observable_subset.mapped_obstacles.append(not_observed_obstacle)


def promote_obstacles(candidate_map: Map, employed_map: Map, promotion_merge_threshold):
    """
    Method to include obstacles from candidate map to employed map
        1. Check if obstacle has been observed more times, then employed map threshold
        2. Check if obstacle can be paired with employed map obstacle
        3.1 If yes, pair with employed map obstacle and increment the observation counter
        3.2 If no, add obstacle to employed map
        3. Remove obstacle from candidate map

    :param employed_map: map containing already mapped obstacles
    :param candidate_map: map containing obstacles with candidate obstacles
    :param promotion_merge_threshold: threshold value to be used for similarity checking
    """

    # find promotable objects
    promotable_obstacles = []
    for obstacle in candidate_map.mapped_obstacles:
        if obstacle.number_of_observations > employed_map.promotion_threshold:
            obstacle.penalty_points = 0
            promotable_obstacles.append(obstacle)

    # find pairings for employed map
    paired_applied_mapped_obstacle_indices, paired_promotable_obstacle_indices = pair_obstacles(
        current_map=employed_map,
        newly_observed_obstacles=promotable_obstacles,
        threshold=promotion_merge_threshold,
    )

    # update paired mapped obstacles
    employed_map.update_map(paired_mapped_obstacles_indices=paired_applied_mapped_obstacle_indices,
                          paired_newly_observed_obstacle_indices=paired_promotable_obstacle_indices,
                          newly_observed_obstacles=promotable_obstacles,
                          promotion=True,
                          )

    # remove paired obstacles from promotable obstacles
    paired_promotable_obstacle_indices.sort()
    for i, index in enumerate(paired_promotable_obstacle_indices):
        candidate_map.mapped_obstacles.remove(promotable_obstacles[index - i])
        promotable_obstacles.pop(index - i)

    # promote the remaining promotable obstacles
    for obstacle in promotable_obstacles:
        employed_map.mapped_obstacles.append(obstacle)
        candidate_map.mapped_obstacles.remove(obstacle)

    # update candidate map length
    candidate_map.number_of_mapped_obstacles = len(candidate_map.mapped_obstacles)
    pass


def pair_obstacles(current_map, newly_observed_obstacles, threshold=0.8):   # TODO optimize threshold value
    """
    Finds the best pairings and returns indices of newly found obstacles

    :param threshold: Threshold value for bad pairings
    :param current_map: instance of map_obstacle.Map class
    :param newly_observed_obstacles: array of instances of map_obstacle.Obstacle class
    :return: 3 values:
                1. paired_mapped_obstacle_indices (Ndarray): indices
                2. paired_new_obstacle_indices (Ndarray): indices of paired obstacle in newly_observed_obstacles
    """

    # calculate cost matrix between the newly observed and the mapped obstacles
    costs, dont_pair = calculate_cost_of_observation(current_map=current_map,
                                                     candidates=newly_observed_obstacles,
                                                     threshold=threshold,
                                                     )

    # find pairings
    paired_mapped_obstacle_indices, paired_newly_observed_obstacle_indices = magyar(costs, maximize=True)

    # remove pairings below threshold
    dont_pair_index = []
    for i, pairing in enumerate(zip(paired_mapped_obstacle_indices, paired_newly_observed_obstacle_indices)):
        if list(pairing) in dont_pair:
            dont_pair_index.append(i)

    paired_mapped_obstacle_indices = np.delete(paired_mapped_obstacle_indices, dont_pair_index)
    paired_newly_observed_obstacle_indices = np.delete(paired_newly_observed_obstacle_indices, dont_pair_index)

    return paired_mapped_obstacle_indices, paired_newly_observed_obstacle_indices


def calculate_rbf(point_1, point_2):
    """
    Calculates the radial basis function between two data points.

    :param point_1: Data point 1 - Obstacle instance
    :param point_2: Data point 2 - Obstacle instance
    :return: rbf between point_1 and point_2
    """

    result = 0

    # check if obstacles are the same type
    if point_1.obstacle_type == point_2.obstacle_type:
        # get numeric parameters into an array
        point_1_params = point_1.strip_params()
        point_2_params = point_2.strip_params()

        # calculate rbf for every numeric parameter
        for i_rbf, sigma in enumerate(sigmas):
            result += math.exp(-((point_1_params[i_rbf] - point_2_params[i_rbf]) ** 2) / (2 * sigma ** 2))

    return result


def calculate_cost_of_observation(current_map, candidates, threshold=0.8):
    """
    Calculate cost matrix of an observation

    :param threshold: threshold value to avoid false pairings
    :param current_map: instance of map_obstacle.Map
    :param candidates: array of instances of map_obstacle.Obstacle class
    :return: 2 values
                1. cost matrix used for the magyar algorithm
                2. forbidden pairing index-couplings
    """
    # initialize dont_pair index-couplings
    dont_pair = []
    # multiply obstacle threshold to all dimensions of an obstacle
    cost_threshold = float(threshold * 5)

    # shape of cost matrix: mapped objs(rows) x candidate objs(columns)
    cost = np.empty((len(current_map.mapped_obstacles), len(candidates)))

    for i, map_point in enumerate(current_map.mapped_obstacles):
        for j, candidate_point in enumerate(candidates):
            cost[i][j] = calculate_rbf(candidate_point, map_point)

            # check if pairing cost is strong enough to be over the threshold
            if cost[i][j] < cost_threshold:
                dont_pair.append([i, j])
                cost[i][j] = 0

    return cost, dont_pair


def turmu_offline_mode_publish(client, topic, number_of_obstacles=3, types=None, like=None):
    new_observation = generate_default_obstacles_list(number_of_obstacles=number_of_obstacles,
                                                      types=types,
                                                      like=like
                                                      )
    for i, obstacle in enumerate(new_observation):

        # publish obstacle over mqtt
        mqtt_turmu.publish_obstacle(client, topic, obstacle)

        # print a debug message
        print(f"obstacle {i + 1} published")


class Egovehicle:
    """
    Class for egovehicle timestamps and sensor locations
    """

    def __init__(self, timestamps=None, sensor_locations=None):
        """
        Method to initialize Egovehicle
        :param timestamps: array of timestamps
        :param sensor_locations: array of sensor locations as [latitude, longitude]
        """
        if sensor_locations is None:
            sensor_locations = []
        if timestamps is None:
            timestamps = []
        self.timestamps = timestamps
        self.sensor_locations = sensor_locations

    def get_published_info(self, client, topic):
        """
        Method that listens to the MQTT broker for egovehicle payloads
        Not used after 30.06.2022.

        :param client: MQTT client
        :param topic: egovehicle topic
        """

        # read egovehicle data, get the one,
        # where the publishing time is closest to the sensor measurement
        client.loop(1)
        mqtt_turmu.subscribe(client=client,
                             topic=topic,
                             timestamps=self.timestamps,
                             sensor_locations=self.sensor_locations
                             )

    def get_sensor_location_at_measurement(self, obstacle: Obstacle):
        """
        Get the sensor location at (or closest to the time of the measurement)
        Not used after 30.06.2022.

        :param obstacle: mo.Obstacle, to which the closest measurement is sought (in time)
        :return: sensor location at the closest measurement
        """
        dt = np.empty(0)
        for timestamp in self.timestamps:
            measurement_timestamp = datetime.datetime.strptime(obstacle.latest_timestamp,
                                                               # "%Y-%m-%dT%H:%M:%S.%fZ",
                                                               "%Y-%m-%dT%H:%M:%SZ",
                                                               )
            current_timestamp = datetime.datetime.strptime(timestamp,
                                                           # "%Y-%m-%dT%H:%M:%S.%fZ",
                                                           "%Y-%m-%dT%H:%M:%SZ",
                                                           )

            dt = np.append(dt, abs(measurement_timestamp - current_timestamp))

        i = dt.argmin()

        sensor_location_at_measurement = self.sensor_locations[i]

        return sensor_location_at_measurement

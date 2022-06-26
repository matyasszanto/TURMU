import csv
import datetime

import numpy as np
import math
from scipy.optimize import linear_sum_assignment as magyar
import json

import mqtt_turmu

# set up sigma parameters for rbf calculation
sigmas = [1,    # sigma_lat
          1,    # sigma_long
          1,    # sigma_speed
          1,    # sigma_width
          1,    # sigma_length
          ]


class Obstacle:
    def __init__(self,
                 object_id=0,
                 object_type="empty",
                 lat=0,
                 long=0,
                 speed=0.0,
                 width=0.0,
                 length=0.0,
                 number_of_observations=1,
                 ):
        """
        Obstacle class

        :param object_id: ID number of object
        :param object_type: type of object: vehicle, pedestrian, not_specified
        :param lat: lateral coordinates of object
        :param long: longitudinal coordinates of object
        :param speed: speed of object
        :param width: width of object
        :param length: length of object
        :param number_of_observations: number of times object has already been observed
        """

        # parameters
        self.obstacle_id = object_id
        self.obstacle_type = object_type  # vehicle, pedestrian, N/S
        self.lat = lat
        self.long = long
        self.speed = speed
        self.width = width
        self.length = length
        self.number_of_observations = number_of_observations

    def print(self):
        """
        print parameters of Obstacle instance
        """
        print(f"Obstacle id:  {self.obstacle_id}")
        print(f"Obstacle type:{self.obstacle_type}")
        print(f"Lateral:      {self.lat}")
        print(f"Longitudinal: {self.long}")
        print(f"Speed:        {self.speed}")
        print(f"Width:        {self.width}")
        print(f"Length:       {self.length}")
        print(f"Observations: {self.number_of_observations}")
        print()

    def strip_params(self):
        """
        Strips the Obstacle instance from its non-numeric parameters (e.g., its ID and its type)

        :return: numpy array of lat, long, speed, width, length
        """
        object_without_id_and_type = np.array([self.lat,
                                               self.long,
                                               self.speed,
                                               self.width,
                                               self.length,
                                               ]
                                              )
        return object_without_id_and_type

    def as_dict(self):
        """
        creates a dictionary from the class parameters

        :return: {"obstacleId": obstacle_id,"type": object_type, "latitude": lat, "longitude": long,
                  "speed": speed, "width": width, "length": length, "observations": no. of observations}
        """

        return {"obstacleId": self.obstacle_id,
                "type": self.obstacle_type,
                "latitude": self.lat,
                "longitude": self.long,
                "speed": self.speed,
                "width": self.width,
                "length": self.length,
                "observations": self.number_of_observations
                }

    def as_json(self):
        object_json = json.dumps(self.as_dict())
        return object_json


def read_obstacles_from_input(input_file=""):
    """
    Read object parameters from input csv file
    TODO changes for actual use-case

    :param input_file: CSV file containing object parameters
    :return: list of objects
    """
    list_of_obstacles = []
    with open(input_file, "r") as file:
        datareader = csv.reader(file)
        for i, row in enumerate(datareader):
            # TODO read input
            list_of_obstacles.append(Obstacle(object_id=i,
                                              # object_type=row.TODO,
                                              # lat=row.TODO,
                                              # long=row.TODO,
                                              # speed=row.TODO,
                                              # width=row.TODO,
                                              # length=row.TODO,
                                              # number_of_observations=row.TODO,
                                              )
                                     )
        return list_of_obstacles


def write_obstacle_to_output(object_full):
    """
    method to write new objects to MQTT or output
    :param object_full: Obstacle instance to write
    """
    # TODO write_object_to_output method

    pass


def generate_default_obstacles_list(number_of_obstacles=3, cars=False):
    """
    Generates a list of Obstacle instances of length number_of_objects with random numeric parameters for
    long and lat, and with fixed values for types

    :param number_of_obstacles: number of objects to be generated
    :param cars: (False) Boolean to select only "other" types of objects or
                randomly choose from [vehicle, pedestrian, other]
    :return: list of Obstacle instances with number of observations set to 5 to show them on the map
    """
    list_of_objects = np.empty(number_of_obstacles, dtype=Obstacle)
    object_types = (np.array(["vehicle", "pedestrian", "other"]) if not cars else np.array(["vehicle"]))
    for i in range(number_of_obstacles):
        current_type = np.random.choice(object_types)
        if current_type == "vehicle":
            current_width = 2
            current_length = 3.5
        elif current_type == "pedestrian":
            current_width = 0.4
            current_length = 0.4
        else:
            current_width = 1
            current_length = 1
        list_of_objects[i] = Obstacle(object_id=i,
                                      object_type=current_type,
                                      lat=10+np.random.uniform(-5, 5),
                                      long=np.random.uniform(-1, 1),
                                      speed=0,
                                      width=current_width,
                                      length=current_length,
                                      number_of_observations=5,
                                      )
    return list_of_objects


class Map:
    def __init__(self, mapped_obstacles, obs_threshold_for_new_obstacle_addition=0):
        """
        Class for mapped obstacles

        :param mapped_obstacles: List of Obstacle instances
        :param obs_threshold_for_new_obstacle_addition: threshold value, denoting
                                                 how many observations shall a new value be added
        """
        self.mapped_obstacles = mapped_obstacles
        self.number_of_mapped_obstacles = len(mapped_obstacles)
        self.obs_threshold_for_new_obstacle_addition = obs_threshold_for_new_obstacle_addition

    def update_map(self, paired_mapped_obstacles_indices, paired_newly_observed_obstacle_indices, newly_observed_obstacles):
        """
        Method for updating means of mapped objects with new observation

        :param paired_mapped_obstacles_indices: output of find_new_objects function
        :param paired_newly_observed_obstacle_indices: output of find_new_objects function
        :param newly_observed_obstacles: array of instances of map_object.Obstacle class
        """
        for i, mapped_obstacle_mean in enumerate(self.mapped_obstacles):

            # check if position update is necessary
            if i in paired_mapped_obstacles_indices:

                # get means and no_observations from paired mapped object
                mapped_means = self.mapped_obstacles[i].strip_params()
                n = self.mapped_obstacles[i].number_of_observations

                # get values from newly observed paired object
                paired_newly_observed_object_index = paired_newly_observed_obstacle_indices[i]
                new_vals = newly_observed_obstacles[paired_newly_observed_object_index].strip_params()

                # calculate new means
                updated_means = np.empty_like(mapped_means)
                for j, (old_val, new_val) in enumerate(zip(mapped_means, new_vals)):
                    weighted_mean = old_val * n
                    updated_means[j] = (weighted_mean + new_val) / (n+1)

                # update mapped object means in map class
                self.mapped_obstacles[i].lat = updated_means[0]
                self.mapped_obstacles[i].long = updated_means[1]
                self.mapped_obstacles[i].speed = updated_means[2]
                self.mapped_obstacles[i].width = updated_means[3]
                self.mapped_obstacles[i].length = updated_means[4]

                # increase number of observations for object
                self.mapped_obstacles[i].number_of_observations += 1

    def add_new_object(self, new_obstacle_indices, newly_observed_obstacles):
        """
        Method to include found new objects into map

        :param new_obstacle_indices: indices of new objects in newly_observed_objects
        :param newly_observed_obstacles: array of instances of map_object.Obstacle class
        """

        # TODO candidate map logic
        for i in new_obstacle_indices:
            self.mapped_obstacles.append(newly_observed_obstacles[i])


def find_new_obstacles(currently_mapped_obstacles, newly_observed_obstacles):
    """
    Finds the best pairings and returns indices of newly found objects

    :param currently_mapped_obstacles: instance of map_object.Map class
    :param newly_observed_objects: array of instances of map_object.Obstacle class
    :return: four values:
                - found_new_object (Boolean): True, if the number of observed objects is greater
                                              than the number of  mapped objects

                - new_object_indices (Ndarray): indices of new objects in newly_observed_objects

                - paired_mapped_object_indices (Ndarray): indices

                - paired_new_object_indices (Ndarray): indices of paired object in newly_observed_objects
    """

    # calculate cost matrix between the newly observed and the mapped objects
    costs = calculate_cost_of_observation(current_map=currently_mapped_obstacles,
                                          candidates=newly_observed_obstacles,
                                          threshold=0.8,  # TODO optimize threshold value
                                          )

    # find pairings
    # TODO set up threshold value for pairings
    paired_mapped_obstacle_indices, paired_newly_observed_obstacle_indices = magyar(costs)

    # TODO logic for found_new_object
    found_new_object = costs.shape[0] != costs.shape[1]

    # TODO find new object indices
    new_object_indices = np.nan

    return found_new_object, new_object_indices, paired_mapped_obstacle_indices, paired_newly_observed_obstacle_indices


def calculate_rbf(point_1, point_2):
    """
    Calculates the radial basis function between two data points.

    :param point_1: Data point 1 - Obstacle instance
    :param point_2: Data point 2 - Obstacle instance
    :return: rbf between point_1 and point_2
    """

    result = 0

    # check if objects are the same type
    if point_1.obstacle_type == point_2.obstacle_type:
        # get numeric parameters into an array
        point_1_params = point_1.strip_params()
        point_2_params = point_2.strip_params()

        # calculate rbf for every numeric parameter
        for i_rbf, sigma in enumerate(sigmas):
            result += math.exp(-((point_1_params[i_rbf] - point_2_params[i_rbf])**2)/(2*sigma**2))

    return result


def calculate_cost_of_observation(current_map, candidates, threshold=0.8):
    """
    Calculate cost matrix of an observation

    :param threshold: threshold value to avoid false pairings
    :param current_map: instance of map_object.Map
    :param candidates: array of instances of map_object.Obstacle class
    :return: cost matrix used for the magyar algorithm
    """
    # multiply object threshold to
    cost_threshold = threshold * 5

    # shape of cost matrix: mapped objs(rows) x candidate objs(columns)
    cost = np.empty((current_map.mapped_obstacles.shape[0], candidates.shape[0]))

    for i, map_point in enumerate(current_map.mapped_obstacles):
        for j, candidate_point in enumerate(candidates):

            # negative sign used because of cost minimization in magyar algorithm
            # while regular Gaussian rbf maximizes at perfect matches
            cost[i][j] = -calculate_rbf(candidate_point, map_point)

    # check if
    cost[cost > cost_threshold] = 0

    return cost


def turmu_offline_mode_publish(client, topic, number_of_obstacles=3, cars=True):
    new_observation = generate_default_obstacles_list(number_of_obstacles=number_of_obstacles, cars=True)
    for obstacle in new_observation:
        obstacle_as_dict = obstacle.as_dict()
        # add a timestamp
        obstacle_as_dict["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        obstacle_as_json = json.dumps(obstacle_as_dict)
        mqtt_turmu.publish_object(client, topic, obstacle_as_json)
        print(f"obstacle {obstacle} published")


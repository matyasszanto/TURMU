import csv
import numpy as np
import math
from scipy.optimize import linear_sum_assignment as magyar


class Object:
    def __init__(self, object_id=0, object_type="empty", lat=0, long=0, speed=0.0, width=0.0, length=0.0):

        # parameters
        self.object_id = object_id
        self.object_type = object_type  # vehicle, pedestrian, N/S
        self.lat = lat
        self.long = long
        self.speed = speed
        self.width = width
        self.length = length

        # Check if object is already in map
        self.new_object = False     # TODO

    def print(self):
        print(f"Object id:    {self.object_id}")
        print(f"Object type:  {self.object_type}")
        print(f"Lateral:      {self.lat}")
        print(f"Longitudinal: {self.long}")
        print(f"Speed:        {self.speed}")
        print(f"Width:        {self.width}")
        print(f"Length:       {self.length}")
        print()

    def strip_params(self):
        object_without_id = np.array([self.lat,
                                      self.long,
                                      self.speed,
                                      self.width,
                                      self.length,
                                      ]
                                     )
        return object_without_id


def read_objects_from_input(input_file=""):
    list_of_objects = []
    with open(input_file, "r") as file:
        datareader = csv.reader(file)
        for i, row in enumerate(datareader):
            # TODO read input
            list_of_objects.append(Object(object_id=i,
                                          # object_type=row.TODO,
                                          # lat=row.TODO,
                                          # long=row.TODO,
                                          # speed=row.TODO,
                                          # width=row.TODO,
                                          # length=row.TODO,
                                          )
                                   )
        return list_of_objects


def generate_default_objects_list(number_of_objects=3):
    list_of_objects = []
    object_types = np.array(["vehicle", "pedestrian", "other"])
    for i in range(number_of_objects):
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
        list_of_objects.append(Object(object_id=i,
                                      object_type=current_type,
                                      lat=10+np.random.uniform(-5, 5),
                                      long=np.random.uniform(-1, 1),
                                      speed=0,
                                      width=current_width,
                                      length=current_length,
                                      )
                               )
    return list_of_objects


class Map:
    def __init__(self, mapped_objects, mapped_objects_means=np.array([]), number_of_observations=1):
        """
        Map Class
        :param mapped_objects: List of mapped objects
        :param mapped_objects_means: means of parameters of mapped objects
        :param number_of_observations: number of observations already added for the objects
        TODO change number_of_observations to be an array for separate objects
        """
        self.mapped_objects = mapped_objects
        self.mapped_objects_means = mapped_objects_means
        self.number_of_observations = number_of_observations

        for i, mapped_object in enumerate(mapped_objects):
            # TODO write mapped_object_mean calculator
            pass

    def update_map(self, paired_mapped_object_indices, paired_newly_observed_object_indices, newly_observed_objects):
        """
        Method for updating means of mapped objects with new observation
        paired_mapped_object_indices: output of find_new_objects function
        paired_newly_observed_object_indices: output of find_new_objects function
        newly_observed_objects: array of instances of map_object.Object class
        """

        for index_to_update_mapped, index_to_update_new in zip(paired_mapped_object_indices,
                                                               paired_newly_observed_object_indices
                                                               ):
            for i, map_mean in enumerate(self.mapped_objects_means[index_to_update_mapped]):
                self.mapped_objects_means[index_to_update_mapped][i] =\
                    (self.number_of_observations * map_mean + newly_observed_objects[index_to_update_new][i]) / \
                    (self.number_of_observations + 1)

        # TODO add number of observations for each object separately

        self.number_of_observations += 1


def find_new_objects(currently_mapped_objects_means, newly_observed_objects):
    """
    Finds the best pairings and returns indices of newly found objects
    currently_mapped_objects_means: instance of map_object.Map.means array
    newly_observed_objects: array of instances of map_object.Object class
    :return: four values:
                - found_new_object (Boolean): True, if the number of observed objects is greater
                                              than the number of  mapped objects

                - new_object_indices (Ndarray): indices of new objects in newly_observed_objects

                - paired_mapped_object_indices (Ndarray): indices

                - paired_new_object_indices (Ndarray): indices of paired object in newly_observed_objects
    """

    costs = calculate_cost_of_observation(currently_mapped_objects_means, newly_observed_objects)
    paired_mapped_object_indices, paired_newly_observed_object_indices = magyar(costs)

    # TODO logic for found_new_object
    found_new_object = costs.shape[0] != costs.shape[1]

    # TODO find new object indices
    new_object_indices = np.nan

    return found_new_object, new_object_indices, paired_mapped_object_indices, paired_newly_observed_object_indices


def calculate_rbf(point_1, point_2, sigma=1):
    """
    Calculates the radial basis function between two data points.
    point_1: Data point 1 - N dimensional array
    point_2: Data point 2 - N dimensional array
    sigma: (Optional) sigma parameter of the Gaussian
    :return: rbf between point_1 and point_2
    """

    result = 0
    for i_rbf in range(point_1.shape[0]):
        result += math.exp(-((point_1[i_rbf] - point_2[i_rbf])**2)/(2*sigma**2))
    return result


def calculate_cost_of_observation(mapped_object_means, candidates, sigma=1):
    """
    Calculate cost of an observation
    TODO finish this help
    :param mapped_object_means:
    :param candidates:
    :param sigma:
    :return:
    """
    cost = np.empty((mapped_object_means.shape[0], candidates.shape[0]))  # mapped objs(rows) x candidate objs(columns)
    for i, map_point in enumerate(mapped_object_means):
        for j, candidate_point in enumerate(candidates):
            # negative sign used because of cost minimization in magyar algorithm
            # while rbf maximizes at perfect matches
            cost[i][j] = -calculate_rbf(candidate_point, map_point, sigma)
    print(cost)
    return cost

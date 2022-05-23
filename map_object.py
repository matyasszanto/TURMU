import csv
import numpy as np


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


def is_new_object(objects_list, new_object_id):
    current_object_new = False
    # TODO if object already exists in map
    return current_object_new

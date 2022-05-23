import map_object as mo


if __name__ == "__main__":

    # Setup local/live mode

    input_available = False    # set to True if file with objects is available
    input_dir = None    # currently takes csv with lines as objects

    # Setup variables

    # Load map objects
    if input_available:
        objects_list = mo.read_objects_from_input(input_dir)

    else:
        objects_list = mo.generate_default_objects_list()



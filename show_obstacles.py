import map_obstacle as mo
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def plot_obstacles(obstacles_list: [mo.Obstacle]):

    lats = list(obst.lat for obst in obstacles_list)
    longs = list(obst.long for obst in obstacles_list)
    ids = list(obst.obstacle_id for obst in obstacles_list)
    ids = [el/len(ids) for el in ids]
    colors = cm.rainbow(ids)

    for lat, long, c in zip(lats, longs, colors):
        plt.scatter(lat, long, color=c)

    plt.show()


if __name__ == "__main__":

    obstacles = mo.generate_default_obstacles_list(number_of_obstacles=100,
                                                   types=["vehicle"],
                                                   )

    plot_obstacles(obstacles)



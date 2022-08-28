import numpy as np

import map_obstacle as mo
import matplotlib.pyplot as plt


def plot_obstacles(obstacles_list,
                   index=0,
                   lat_extremes=None,
                   long_extremes=None,
                   path="plots",
                   colors=None,
                   ego_pos=None
                   ):

    if ego_pos is None:
        ego_pos = []
    if colors is None:
        colors = []
    if long_extremes is None:
        long_extremes = [-10, 10]
    if lat_extremes is None:
        lat_extremes = [-10, 10]

    lats = list(obst.lat for obst in obstacles_list)
    longs = list(obst.long for obst in obstacles_list)
    ids = list(obst.obstacle_id for obst in obstacles_list)
    if (np.array(ids) == np.zeros(len(obstacles_list))).all():
        ids = np.linspace(0, len(obstacles_list)-1, num=len(obstacles_list))/len(ids)
    else:
        ids = [el/len(ids) for el in ids]

    # colors = cm.rainbow(ids)

    fig, ax = plt.subplots()
    ax.set(xlim=(lat_extremes[0], lat_extremes[1]), ylim=(long_extremes[0], long_extremes[1]))
    ax.set_xlabel("lateral")
    ax.set_ylabel("longitudinal")

    # for lat, long, idx in zip(lats, longs, list(obst.obstacle_id for obst in obstacles_list)):
    #     ax.scatter(lat, long, c=idx)

    ax.scatter(lats, longs, c=colors[:len(lats)])
    ax.scatter(ego_pos[0], ego_pos[1], marker="*")

    plt.savefig(f"{path}/{index}.png")
    # plt.show()
    plt.cla()


if __name__ == "__main__":

    obstacles = mo.generate_default_obstacles_list(number_of_obstacles=4,
                                                   types=["vehicle"],
                                                   )

    plot_obstacles(obstacles)

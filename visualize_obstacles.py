import datetime

import numpy as np

import map_obstacle as mo
import matplotlib.pyplot as plt
from matplotlib import cm


def plot_obstacles(obstacles_list,
                   index=0,
                   lat_extremes=None,
                   long_extremes=None,
                   path="plots",
                   colors=None,
                   ego_pos=None,
                   map_type="",
                   observable_radius=0,
                   ):

    if ego_pos is None:
        ego_pos = [0, 0]
    if colors is None:
        colors = cm.tab20c(np.linspace(0, 1, len(obstacles_list) + 10))
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
    ax.set_title(map_type, fontsize=16)
    ax.set(xlim=(lat_extremes[0],   # + 0.00015,
                 lat_extremes[1]),  # - 0.00016),
           ylim=(long_extremes[0],  # + 0.0002,
                 long_extremes[1])  # + 0.00005)
           )
    ax.set_xlabel("latitude (°)", fontsize=15)
    ax.set_ylabel("longitude (°)", fontsize=15)
    plt.tight_layout()

    # for lat, long, idx in zip(lats, longs, list(obst.obstacle_id for obst in obstacles_list)):
    #     ax.scatter(lat, long, c=idx)

    ax.scatter(lats, longs, c=colors[:len(lats)])
    ax.scatter(ego_pos[0], ego_pos[1], marker="*", s=[150])
    # if observable_radius > 0:
        # cir = plt.Circle((ego_pos[0], ego_pos[1]), observable_radius, color='b', fill=False)
        # ax.add_patch(cir)

    plt.savefig(f"{path}/{index}_{datetime.datetime.now()}.png")
    # plt.show()
    fig.clf()
    plt.close()


if __name__ == "__main__":

    obstacles = mo.generate_default_obstacles_list(types=["vehicle"],
                                                   like=[mo.Obstacle(), mo.Obstacle(), mo.Obstacle(), mo.Obstacle()],
                                                   )

    plot_obstacles(obstacles)

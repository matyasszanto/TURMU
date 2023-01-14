import numpy as np
import pandas as pd
from haversine import haversine, Unit

positions = np.loadtxt("positions_employed_9.csv", delimiter=";")

dists = []
# deltas = []
for i in range(len(positions) - 1):
    dist = haversine((positions[i, 0], positions[i, 1]),
                     (positions[i+1, 0], positions[i+1, 1]),
                     unit=Unit.METERS
                     )
    # dist_lat = positions[i, 0] - positions[i+1, 0]
    # dist_long = positions[i, 1] - positions[i+1, 1]
    # deltas.append(np.sqrt(dist_lat**2 + dist_long**2))
    dists.append(dist)

print(np.sum(dists))

df = pd.DataFrame([np.average(dists), np.var(dists)])
df.to_clipboard(index=False, header=None, sep=None)
print(f"Printed to clipboard\n{df.head()}")


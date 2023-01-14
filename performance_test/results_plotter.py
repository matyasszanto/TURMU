import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FormatStrFormatter

arr = pd.read_csv("results_condensed.csv", delimiter=";").to_numpy()

fig, ax = plt.subplots()
ax.plot(arr[:, 0], arr[:, 1], "bo-")
ax.set_xlabel("Promotion threshold")
ax.set_ylabel("Total jitter (m)")
# ax.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
ax2 = ax.twinx()
ax2.plot(arr[:, 0], arr[:, 2], "go-")
ax2.set_ylabel("Average time delay (s)")
# ax2.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
# plt.show()
plt.savefig("performance_test_results.png")

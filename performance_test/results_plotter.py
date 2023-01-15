import matplotlib.pyplot as plt
import pandas as pd

arr = pd.read_csv("results_condensed.csv", delimiter=";").to_numpy()

fig, ax = plt.subplots()
plt1 = ax.plot(arr[:, 0], arr[:, 1], "bo-", label="Jitter")
ax.set_xlabel("Promotion threshold", fontsize=15)
ax.set_ylabel("Total jitter (m)", fontsize=15)
ax2 = ax.twinx()
plt2 = ax2.plot(arr[:, 0], arr[:, 2], "go-", label="Delay")
ax2.set_ylabel("Average time delay (s)", fontsize=15)

plts = plt1 + plt2
labs = [plot.get_label() for plot in plts]
ax.legend(plts, labs, loc="upper center")

plt.tight_layout()
# plt.show()
plt.savefig("performance_test_results_new.png")

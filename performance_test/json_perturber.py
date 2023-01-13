import numpy as np
import json

with open("perf_test.json", "r") as file:
    perf_test = json.load(file)
    print(perf_test)

for pub in perf_test:
    obsts = pub['obstacles']
    for obst in obsts:
        obst['latitude'] = obst['latitude'] + np.random.randn()*1e-5
        obst['longitude'] = obst['longitude'] + np.random.randn()*1e-5

perf_test_string = json.dumps(perf_test, indent=4)
with open("perf_test.json", "w") as file:
    file.write(perf_test_string)

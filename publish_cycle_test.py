import time

import mqtt_publish_ego_test
import mqtt_publish_test

if __name__ == "__main__":

    mqtt_publish_test.run(number_of_obstacles=2)

    time.sleep(0.4)

    mqtt_publish_ego_test.run()

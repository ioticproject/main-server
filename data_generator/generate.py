import json
import time

import requests

from config import Config
from utils import Utils


class Generator():
    @staticmethod
    def generate_data(time_interval):
        id_user = Utils.post_user()
        id_device = Utils.post_device(id_user)
        id_sensor = Utils.post_sensor(id_user, id_device, "temp", "C")
        while True:
            id_data = Utils.post_data(id_sensor, 100)
            time.sleep(time_interval)


if __name__ == "__main__":
    Generator.generate_data(0.5)

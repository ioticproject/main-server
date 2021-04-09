import json
import logging
import random
import string
from http import HTTPStatus

import requests

from config import Config


class Utils:

    @staticmethod
    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    

    @staticmethod
    def post_user():
        # logger = logging.getLogger('')
        username=Utils.generate_random_string(10)
        payload = "{ \"name\": \"" + username + "\", \"password\": \"!!new_Password\", \"email\": \"" + username + "@gmail.com\"}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", Config.USER_URL, headers=headers, data=payload)

        try:
            response.status_code == HTTPStatus.CREATED
        except Valueerror:
            print("[ERROR] Could not add the new user.")

        id = json.loads(response.text.replace("\'", "\"")).get('id')
        print("[INFO] Added user %s with id %s." % (username, id))
        return id


    @staticmethod
    def post_device(id_user):
        device_name = Utils.generate_random_string(10)
        payload="{ \"name\": \"" + device_name + "\", \"id_user\": \"" + id_user + "\"}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", Config.DEVICE_URL, headers=headers, data=payload)

        try:
            response.status_code == HTTPStatus.CREATED
        except Valueerror:
            print("[ERROR] Could not add the new device.")

        id = json.loads(response.text.replace("\'", "\"")).get('id')
        print("[INFO] Added device %s with id %s." % (device_name, id))
        return id


    @staticmethod
    def post_sensor(id_user, id_device, type, measure_unit):
        payload="{ \"type\": \"" + type + "\", \"measure_unit\": \"" + measure_unit + "\", \"id_user\": " + id_user + ", \"id_device\": " + id_device + "}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", Config.SENSOR_URL, headers=headers, data=payload)

        try:
            response.status_code == HTTPStatus.CREATED
        except Valueerror:
            print("[ERROR] Could not add the new sensor.")

        id = json.loads(response.text.replace("\'", "\"")).get('id')
        print("[INFO] Added sensor with type %s and id %s." %(type, id))
        return id
    
    @staticmethod
    def post_data(id_sensor, value):
        payload="{ \"id_sensor\": " + id_sensor + ", \"value\": " + str(value) + "}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", Config.DATA_URL, headers=headers, data=payload)

        try:
            response.status_code == HTTPStatus.CREATED
        except Valueerror:
            print("[ERROR] Could not add the new data.")

        id = json.loads(response.text.replace("\'", "\"")).get('id')
        print("[INFO] Added data for sensor with id %s." %(id_sensor))
        return id

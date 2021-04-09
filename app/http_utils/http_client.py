import logging
import os
from http import HTTPStatus

import requests


class Client():
    @staticmethod
    def generate_auth_token(username, password):
        url = os.getenv("AUTH_URL")

        # payload=r"{\"username\": \"{username}\", \"password\": \"{password}\"\r\n}".format(username=username, password=password)
        payload = "{\"username\": \"" + username +  "\", \"password\": \"" + password + "\"}"

        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != HTTPStatus.OK:
            logging.info("[ERROR] Something is wrong with the authentication service.")

        return response.json().get("access_token")

    @staticmethod
    def trigger(id_user, id_sensor, value):
        url = os.getenv("TRIGGER_ROUTE").format(ID_USER=id_user, ID_SENSOR=id_sensor)

        payload = "{\"value\": " + str(value) + "}"

        headers = {
        'Content-Type': 'application/json'
        }

        response = None

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except:
            print("[ERROR] Processing Service is unreachable.")

        if response and response.status_code != HTTPStatus.OK:
            logging.info("[ERROR] Error triggering the Processing Service.")

        return

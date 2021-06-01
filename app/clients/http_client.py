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

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != HTTPStatus.OK:
            logging.info("[ERROR] Something is wrong with the authentication service.")

        return response.json().get("access_token")

import json
import sys, os
from http import HTTPStatus
import time
import requests

from flask import (Response, jsonify, request)

sys.path.append('..\\')
from models.device import Device
from models.sensor import Sensor
from models.user import User
from utils import (device_id_exists,
                   get_new_id,
                   get_new_device_api_key,
                   user_id_exists,
                   format_timestamp,
                   get_device_apiKey)
from validation import check_device_post, check_device_put

from routes.sensor_routes import delete_sensor, add_sensor
from routes.data_routes import add_data


def sync():
    apiKey = request.headers.get('apiKey')

    if not get_device_apiKey(apiKey):
        return {'error': "The apiKey is not associated with a device."}, HTTPStatus.UNAUTHORIZED

    return str(int(time.time())), HTTPStatus.OK


def put_device():
    body = request.get_json()

    apiKey = request.headers.get('apiKey')
    device = get_device_apiKey(apiKey)
    if not device:
        return {'error': "The apiKey is not associated with a device."}, HTTPStatus.UNAUTHORIZED

    device_body = {}
    if body.get('name'):
        device_body['name'] = body.get('name')
    if body.get('description'):
        device_body['description'] = body.get('description')

    Device.objects.get(apiKey=apiKey).update(**device_body)

    sensors = body.get('sensors')
    if sensors:
        for sensor in sensors:
            msg, status_code = add_sensor(device.id_user,
                       device.id,
                       sensor)
            if (status_code != HTTPStatus.CREATED):
                return msg, status_code

    return '', HTTPStatus.OK


def put_data():
    body = request.get_json()

    apiKey = request.headers.get('apiKey')
    device = get_device_apiKey(apiKey)
    if not device:
        return {'error': "The apiKey is not associated with a device."}, HTTPStatus.UNAUTHORIZED

    for data in body:
        # if (data.value > 20):
        #     serverToken = os.getenv("FIREBASE_TOKEN")
        #     headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization': 'key=' + serverToken,
        #     }

        #     deviceToken='cQ4hhDG-Ri6b41j07-MqIS:APA91bHX3vrPJgNpdSIZxDZ-AqydpLh_n7p_9mSLbenkW42iaag_dDRM2gTAhchv7NhX5Xy_ALtMAte6G9ViSNw41usxvoBxLyUjoVQrnaCIIzpnMtFSKW7twmk1HouT0aTrALp2EQIO'

        #     body = {
        #             'notification': {'title': 'Sending push form python script',
        #                              'body': 'New Message'},
        #             'to': deviceToken,
        #             'priority': 'high',
        #             #   'data': dataPayLoad,
        #             }
        #     response = requests.post("https://fcm.googleapis.com/fcm/send",
        #                              headers=headers,
        #                              data=json.dumps(body))
        #     print(response.status_code)
        #     print(response.json())

        msg, status_code = add_data(data.get("id_sensor"), data, device.id_user, device.id)
        if (status_code != HTTPStatus.CREATED):
            return msg, status_code

    return '', HTTPStatus.OK


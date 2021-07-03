import json
import sys, os
from http import HTTPStatus
import time
import logging

from flask import request

sys.path.append('..\\')
from models.device import Device
from utils import (
    get_device_apiKey,
    get_sensor_by_name
)

from models.sensor import Sensor
from models.actor import Actor

from routes.device_routes import get_device
from routes.actor_routes import add_actor
from routes.sensor_routes import add_sensor
from routes.data_routes import add_data


def sync():
    apiKey = request.headers.get('apiKey')

    if not get_device_apiKey(apiKey):
        return {'error': "The apiKey is not associated with a device."}, HTTPStatus.UNAUTHORIZED

    return str(int(time.time())), HTTPStatus.OK


def put_device(auth):
    body = request.get_json()

    apiKey = request.headers.get('apiKey')
    device = get_device_apiKey(apiKey)
    if not device:
        return {'error': "The apiKey is not associated with a device."}, HTTPStatus.UNAUTHORIZED

    # auth.grantPublish({
    #         "token": apiKey,
    #         "pattern": device.id_user + '.' + device.id + '.*'
    #     })

    device_body = {}
    if body.get('name'):
        device_body['name'] = body.get('name')
    if body.get('description'):
        device_body['description'] = body.get('description')

    Device.objects.get(apiKey=apiKey).update(**device_body)
    Sensor.objects.filter(id_device=device.id).delete()
    Actor.objects.filter(id_device=device.id).delete()

    sensors = body.get('sensors')
    if sensors:
        for sensor in sensors:
                msg, status_code = add_sensor(device.id_user,
                           device.id,
                           sensor)
                if (status_code != HTTPStatus.CREATED):
                    return msg, status_code

    actors = body.get('actors')
    if actors:
        for actor in actors:
            msg, status_code = add_actor(device.id_user,
                       device.id,
                       actor)

            if (status_code != HTTPStatus.CREATED):
                return msg, status_code

    return 'ok', HTTPStatus.OK


def recv_data(msg):
    ids = msg['topic'].split('.')
    id_device = ids[0]
    device = get_device(id_device)[0]
    sensor = get_sensor_by_name(ids[1], device['id_user'], id_device)

    if not sensor:
        return

    data = json.loads(msg['data'])

    if data['type'] != "int" and data['type'] != "double":
        return

    del data['type']
    del data['time']

    msg, status_code = add_data(sensor.id, data, device['id_user'], id_device)
    if (status_code != HTTPStatus.CREATED):
        logging.error(msg)
    print(msg)

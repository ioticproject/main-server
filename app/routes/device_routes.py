import json
import sys
from http import HTTPStatus
import datetime

from flask import (Response, jsonify, request)

sys.path.append('..\\')
from models.device import Device
from models.sensor import Sensor
from models.user import User
from utils import (device_id_exists,
                   get_new_id,
                   get_new_device_api_key,
                   user_id_exists,
                   format_timestamp)
from validation import check_device_post, check_device_put

from routes.sensor_routes import delete_sensor


def get_device(id):
    devices = Device.objects.filter(id=id)
    if len(devices) == 0:
        return {'error': "The device id does not exist."}, HTTPStatus.NOT_FOUND
    device = devices.get(0)
    sensors = Sensor.objects.filter(id_device=id)

    ret = {
        '_id': device.id,
        'name': device.name,
        'description': device.description,
        'id_user': device.id_user,
        'timestamp': device.timestamp,
        'sensors': format_timestamp(sensors)
        }

    return ret, HTTPStatus.OK


def get_user_devices(id_user):
    if not user_id_exists(id_user):
        return {'error': "The user id does not exist."}, HTTPStatus.NOT_FOUND
    devices = Device.objects.filter(id_user=id_user)

    return {'devices': format_timestamp(devices)}, HTTPStatus.OK


def get_devices():
    devices = Device.objects()

    return {'devices': format_timestamp(devices)}, HTTPStatus.OK



def add_device(id_user):
    body = request.get_json()

    resp = check_device_post(body, id_user)

    if resp:
        return resp

    if not body.get('id'):
        body["id"] = get_new_id()

    if "timestamp" in body.keys():
        time = body["timestamp"]
        body.update({"timestamp": datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')})

    body['apiKey'] = get_new_device_api_key()
    device = Device(**body).save()

    id = device.id
    return {'_id': str(id), 'apiKey': device.apiKey}, HTTPStatus.CREATED


def update_device(id_user, id):
    body = request.get_json()
    resp = check_device_put(body, id, id_user)

    if resp:
        return resp

    Device.objects.get(id=id).update(**body)
    return '', HTTPStatus.OK


def delete_device(id_user, id):
    if not user_id_exists(id_user):
        return {'error': "The user id does not exist."}, HTTPStatus.NOT_FOUND

    if not device_id_exists(id, id_user):
        return {'error': 'The device id does not exist.'}, HTTPStatus.NOT_FOUND

    sensors = Sensor.objects.filter(id_device=id)
    for sensor in sensors:
        delete_sensor(id_user, id, sensor.id)

    Device.objects.get(id=id).delete()
    return '', HTTPStatus.OK

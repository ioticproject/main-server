import sys
from http import HTTPStatus
import datetime
from flask import request

sys.path.append('..\\')
from models.data import Data
from models.sensor import Sensor
from utils import (device_id_exists,
                   get_new_id,
                   sensor_id_exists,
                   user_exists,
                   user_id_exists,
                   format_timestamp)
from validation import check_sensor_post, check_sensor_put
from routes.data_routes import delete_data


def get_sensor(id):
    sensors = Sensor.objects.filter(id=id)
    if len(sensors) == 0:
        return {'error': "The sensor id does not exist."}, HTTPStatus.NOT_FOUND
    sensor = sensors.get(0)
    data = Data.objects.filter(id_sensor=id)
    ret = {
        '_id': sensor.id,
        'id_device': sensor.id_device,
        'id_user': sensor.id_user,
        'type': sensor.type,
        'measure_unit': sensor.measure_unit,
        'timestamp': sensor.timestamp,
        # 'data': data
        }

    return ret, HTTPStatus.OK


def get_sensors():
    sensors = Sensor.objects()

    return {'sensors': format_timestamp(sensors)}, HTTPStatus.OK


def get_user_sensors(id_user):
    if not user_id_exists(id_user):
        return {'error': "The user id does not exist."}, HTTPStatus.NOT_FOUND
    sensors = Sensor.objects.filter(id_user=id_user)

    return {'sensors': format_timestamp(sensors)}, HTTPStatus.OK


def get_device_sensors(id_device, id_user):
    if not device_id_exists(id_device, id_user):
        return {'error': "One of the user and device id does not exist."}, HTTPStatus.NOT_FOUND
    sensors = Sensor.objects.filter(id_device=id_device)

    return {'sensors': format_timestamp(sensors)}, HTTPStatus.OK



def add_sensor(id_user, id_device, body):
    resp = check_sensor_post(body, id_user, id_device)

    if resp:
        return resp

    if not body.get('id'):
        body["id"] = get_new_id()

    if "timestamp" in body.keys():
        time = body["timestamp"]
        body.update({"timestamp": datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')})
    sensor = Sensor(**body).save()

    id = sensor.id
    return {'_id': str(id)}, HTTPStatus.CREATED


def update_sensor(id_user, id_device, id):
    body = request.get_json()
    resp = check_sensor_put(body, id,  id_user, id_device)

    if resp:
        return resp

    Sensor.objects.get(id=id).update(**body)
    return '', HTTPStatus.OK


def delete_sensor(id_user, id_device, id):
    if not sensor_id_exists(id, id_user, id_device):
        return {'error': 'Sensor id not found'}, HTTPStatus.NOT_FOUND

    data = Data.objects.filter(id_sensor=id)
    for d in data:
        delete_data(d.id)

    Sensor.objects.get(id=id).delete()
    return '', HTTPStatus.OK

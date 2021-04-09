import json
import sys
from http import HTTPStatus
import datetime
from flask import Response, jsonify, request
import requests
from http_utils.http_client import Client

sys.path.append('..\\')
from models.data import Data
from utils import (check_data,
                   check_date,
                   data_id_exists,
                   get_new_id,
                   sensor_id_exists,
                   format_timestamp)
from validation import check_data_post


def get_data():
    data = Data.objects()

    return {'data': format_timestamp(data)}, HTTPStatus.OK



def get_sensor_data(id_user, id_device, id_sensor):
    if not sensor_id_exists(id_sensor, id_user, id_device):
        return {'error': "The sensor id does not exist."}, HTTPStatus.NOT_FOUND

    data = Data.objects.filter(id_sensor=id_sensor)

    return {'data': format_timestamp(data)}, HTTPStatus.OK


def get_filtered_sensor_data(id_user, id_device, id_sensor):
    if not sensor_id_exists(id_sensor, id_user, id_device):
        return {'error': "The sensor id does not exist."}, HTTPStatus.NOT_FOUND

    min_value = request.args.get('min_value')
    max_value = request.args.get('max_value')

    from_date = request.args.get('from')
    to_date = request.args.get('until')

    if from_date and check_date(from_date):
        return str([]), HTTPStatus.OK

    if to_date and check_date(to_date):
        return str([]), HTTPStatus.OK

    data = Data.objects().filter(id_sensor=id_sensor)
    if not data:
        return str([]), HTTPStatus.OK

    res = []

    for d in data:
        if check_data(d,
                      min_value=min_value,
                      max_value=max_value,
                      from_date=from_date,
                      to_date=to_date):
            res.append(d)

    return {"data": format_timestamp(res)}, HTTPStatus.OK


def add_data(id_sensor, body, id_user, id_device):
    resp = check_data_post(body, id_user, id_device, id_sensor)

    if resp:
        return resp

    body["id"] = get_new_id()
    if "timestamp" in body.keys():
        time = body["timestamp"]
        body.update({"timestamp": datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')})
    data = Data(**body).save()

    Client.trigger(id_user, id_sensor, body["value"])

    id = data.id
    return {'_id': str(id)}, HTTPStatus.CREATED


def delete_data(id):
    if not data_id_exists(id):
        return {'error': 'Data id not found'}, HTTPStatus.NOT_FOUND

    Data.objects.get(id=id).delete()
    return '', HTTPStatus.OK

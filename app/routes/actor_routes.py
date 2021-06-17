import sys
from http import HTTPStatus
import datetime
from flask import request

sys.path.append('..\\')
from models.user import User
from models.data import Data
from models.actor  import Actor
from models.notification import Notification

from utils import (device_id_exists,
                   get_new_id,
                   user_exists,
                   user_id_exists,
                   format_timestamp)

from routes.data_routes import delete_data
from send_email.email_notification import send_notification_email



def get_actor(id):
    actors = Actor.objects.filter(id=id)
    if len(actors) == 0:
        return {'error': "The actor id does not exist."}, HTTPStatus.NOT_FOUND
    actor = actors.get(0)
    data = Data.objects.filter(id_actor=id)
    ret = {
        '_id': actor.id,
        'id_device': actor.id_device,
        'id_user': actor.id_user,
        'type': actor.type,
        'measure_unit': actor.measure_unit,
        'timestamp': actor.timestamp,
        # 'data': data
        }

    return ret, HTTPStatus.OK


def get_actors():
    actors = Actor.objects()

    return {'actors': format_timestamp(actors)}, HTTPStatus.OK


def get_user_actors(id_user):
    if not user_id_exists(id_user):
        return {'error': "The user id does not exist."}, HTTPStatus.NOT_FOUND
    actors = Actor.objects.filter(id_user=id_user)

    return {'actors': format_timestamp(actors)}, HTTPStatus.OK


def get_device_actors(id_device, id_user):
    if not device_id_exists(id_device, id_user):
        return {'error': "One of the user and device id does not exist."}, HTTPStatus.NOT_FOUND
    actors = Actor.objects.filter(id_device=id_device)

    return {'actors': format_timestamp(actors)}, HTTPStatus.OK



def add_actor(id_user, id_device, body):
    # resp = check_actor_post(body, id_user, id_device)
    #
    # if resp:
    #     return resp

    if not body.get('id'):
        body["id"] = get_new_id()

    if "timestamp" in body.keys():
        time = body["timestamp"]
        body.update({"timestamp": datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')})
    actor = Actor(**body).save()
    user = User.objects.filter(id=id_user)[0]

    message = "[ACTOR \"" + actor.name + "\"] Successfully added a new actor."
    json = {"id": get_new_id(),
            "id_user": id_user,
            "id_sensor": "None",
            "message": message,
            "severity": 'success'}
    Notification(**json).save()
    send_notification_email(user.email, message, 'success')

    id = actor.id
    return {'_id': str(id)}, HTTPStatus.CREATED


def update_actor(id_user, id_device, id):
    body = request.get_json()
    # resp = check_actor_put(body, id,  id_user, id_device)
    #
    # if resp:
    #     return resp

    Actor.objects.get(id=id).update(**body)
    return '', HTTPStatus.OK


def delete_actor(id_user, id_device, id):
    # if not actor_id_exists(id, id_user, id_device):
    #     return {'error': 'Actor id not found'}, HTTPStatus.NOT_FOUND

    data = Data.objects.filter(id_actor=id)
    for d in data:
        delete_data(d.id)

    Actor.objects.get(id=id).delete()
    return '', HTTPStatus.OK

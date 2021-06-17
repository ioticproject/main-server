import sys
from http import HTTPStatus
from flask import request

sys.path.append('..\\')

from models.message import Message
from models.user import User
from models.notification import Notification

from utils import get_new_id


def get_messages():
    messages = Message.objects()
    return {'messages': messages}, HTTPStatus.OK


def add_message():
    body = request.get_json()

    if not body.get('id'):
        body["id"] = get_new_id()

    message = Message(**body).save()

    user = User.objects().filter(name=message.username)[0]

    msg = "Your message was successfully sent to support service."
    json = {"id": get_new_id(),
            "id_user": user.id,
            "id_sensor": "None",
            "message": msg,
            "severity": 'info'}
    Notification(**json).save()

    return '',  HTTPStatus.CREATED


def edit_message(id):
    body = request.get_json()
    body['read'] = True

    message = Message.objects.get(id=id).update(**body)
    user = User.objects().filter(name=message.username)[0]

    msg = "You received a new message from the support service."
    json = {"id": get_new_id(),
            "id_user": user.id,
            "id_sensor": "None",
            "message": msg,
            "severity": 'info'}
    Notification(**json).save()

    return '',  HTTPStatus.CREATED


def faq_message(id):
    faq = {'faq': True}

    Message.objects.get(id=id).update(**faq)
    return '',  HTTPStatus.CREATED


def get_faq_messages():
    messages = Message.objects().filter(faq=True)
    return {'messages': messages}, HTTPStatus.OK


def delete_message(id):
    Message.objects.get(id=id).delete()
    return '', HTTPStatus.OK

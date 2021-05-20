import sys
from http import HTTPStatus
from flask import Response, request

sys.path.append('..\\')

from models.message import Message
from utils import get_new_id


def get_messages():
    messages = Message.objects()
    return {'messages': messages}, HTTPStatus.OK


def add_message():
    body = request.get_json()

    if not body.get('id'):
        body["id"] = get_new_id()

    message = Message(**body).save()
    return '',  HTTPStatus.CREATED


def delete_user(id):
    Message.objects.get(id=id).delete()
    return '', HTTPStatus.OK

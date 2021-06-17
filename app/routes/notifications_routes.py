import sys
from http import HTTPStatus
from flask import request

sys.path.append('..\\')

from models.notification import Notification
from utils import get_new_id

def add_notification(id_user, id_sensor, message, severity):
    body = request.get_json()

    if not body.get('id'):
        body["id"] = get_new_id()

    message = Notification(**body).save()
    return '',  HTTPStatus.CREATED


def get_user_notifications(id):
    notifications = Notification.objects().filter(id_user=id)
    return {'notifications': notifications}, HTTPStatus.OK

def delete_user_notifications(id):
    notifications = Notification.objects.filter(id_user=id)

    for notification in notifications:
        Notification.objects.get(id=notification.id).delete()

    return '', HTTPStatus.OK

import json
import sys, os
from http import HTTPStatus
import datetime
from flask import Response, request
import requests

sys.path.append('..\\')
from models.firebaseToken import FirebaseToken


def send_notifications(id_user):
    body = request.get_json()
    notification_type = body.get("type")
    message = body.get("message")

    body = {
          'notification': {'title': 'Sending push form python script',
                           'body': message},
          'to': None,
          'priority': 'high',
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + os.getenv("FIREBASE_TOKEN"),
    }

    if notification_type == "push":
        tokens = FirebaseToken.objects.filter(id_user=id_user)

        for token in tokens:
            body.update({'to': token.firebaseToken})
            response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))

    return {}, HTTPStatus.OK

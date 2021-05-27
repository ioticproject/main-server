import sys
import os
from http import HTTPStatus
import re

from flask import Response, request, jsonify

sys.path.append('..\\')

from send_email.email_notification import send_confirmation_email, send_reset_password_email
from exceptions.email_exception import EmailOperationError
from http_utils.http_client import Client
from models.firebaseToken import FirebaseToken
from models.device import Device
from models.sensor import Sensor
from models.user import User
from security.security import encode_password, encode_reset_password_code
from utils import get_new_id, user_id_exists, format_timestamp, get_new_reset_password_code
from validation import check_user_post, check_user_put, password_regex
from routes.device_routes import delete_device


def welcome(username):
    body = {"confirmed": True}
    User.objects.get(name=username).update(**body)

    return Response("Welcome, " + username + "! :)",
                    mimetype="application/json",
                    status=HTTPStatus.OK)


def unsubscribe(username):
    return Response("Sorry to see you go, " + username + "... :(",
                    mimetype="application/json",
                    status=HTTPStatus.OK)


def get_users():
    users = User.objects()
    return {'users': users}, HTTPStatus.OK


def login_user():
    body = request.get_json()
    username = body.get('username')
    password = body.get('password')

    encoded_password = encode_password(password)

    users = User.objects.filter(name=username, password=encoded_password)

    if len(users) == 0:
        return str({'error': 'Invalid credentials.'}), HTTPStatus.UNAUTHORIZED

    user = users[0]
    if not user.confirmed:
        return str({'error': 'Please check your email and confirm your account.'}), HTTPStatus.UNAUTHORIZED

    access_token = Client.generate_auth_token(username=username,
                                              password=password)
    if access_token is None:
        return str({'error': 'Something went wrong with the authentication service.'}), HTTPStatus.SERVICE_UNAVAILABLE

    return {
        'username': user.name,
        'password': password,
        'email': user.email,
        '_id': user.id,
        'access_token': access_token,
        'role': user.role}, HTTPStatus.CREATED


def add_user():
    body = request.get_json()
    body['name'] = body.get('username')
    del body['username']

    resp = check_user_post(body)

    if resp:
        return resp

    if not body.get('id'):
        body["id"] = get_new_id()

    password = body["password"]
    del body["password"]
    body["password"] = encode_password(password)
    user = User(**body).save()

    access_token = Client.generate_auth_token(username=user.name,
                                              password=password)
    if access_token is None:
        return str({'error': 'Something went wrong with the authentication service.'}), HTTPStatus.SERVICE_UNAVAILABLE

    ret = {
        'username': user.name,
        'password': password,
        'email': user.email,
        '_id': user.id,
        'access_token': access_token,
        'role': user.role}, HTTPStatus.CREATED
    try:
        send_confirmation_email(user.email, user.name, str(user.id))
        return ret

    except EmailOperationError:
        return ret


def generate_reset_password_code():
    body = request.get_json()
    credential = body.get('credential')

    users = User.objects.filter(email=credential)
    if not users:
        users = User.objects.filter(name=credential)
        if not users:
            return {"error": "This email/username was not associated with an IoTIC account."}, HTTPStatus.NOT_FOUND

    user = users.get(0)
    resetPasswordCode = get_new_reset_password_code()

    send_reset_password_email(user.email, user.name, resetPasswordCode)
    User.objects.get(id=user.id).update(**{'resetPasswordCode': encode_reset_password_code(resetPasswordCode)})
    return "", HTTPStatus.OK


def reset_password():
    body = request.get_json()
    resetPasswordCode = body.get('resetPasswordCode')
    credential = body.get('credential')

    users = User.objects.filter(email=credential)
    if not users:
        users = User.objects.filter(name=credential)
        if not users:
            return {"error": "This email/username was not associated with an IoTIC account."}, HTTPStatus.NOT_FOUND

    user = users.get(0)

    if user.resetPasswordCode != "Undefined":
        if encode_reset_password_code(resetPasswordCode) == user.resetPasswordCode:
            new_password = body.get('newPassword')

            if not new_password:
                return {"error": "The new password is missing."}, HTTPStatus.BAD_REQUEST

            if not re.fullmatch(password_regex, new_password):
                return {'error': 'The password format is invalid. It must contain at least 8 symbols.'}, HTTPStatus.BAD_REQUEST

            password = encode_password(new_password)
            if password == user.password:
                return {'error': 'The new password must be different from the old one.'}, HTTPStatus.BAD_REQUEST

            user.update(**{'password': password, 'resetPasswordCode': 'Undefined'})
        else:
            return {"error": "Invalid code."}, HTTPStatus.UNAUTHORIZED

        return "", HTTPStatus.OK
    else:
        return {"error": "There is no reset password code. Please generate one."}, HTTPStatus.UNAUTHORIZED


def get_user(id):
    user = User.objects.filter(id=id).get(0)
    devices = Device.objects.filter(id_user=id)
    sensors = Sensor.objects.filter(id_user=id)
    ret = {
        '_id': user.id,
        'name': user.name,
        'email': user.email,
        'devices': format_timestamp(devices),
        'sensors': format_timestamp(sensors)
        }

    return ret, HTTPStatus.OK



def update_user(id):
    body = request.get_json()
    resp = check_user_put(body, id)

    if resp:
        return resp

    password = body.get('password')
    del body["password"]
    body["password"] = encode_password(password)

    User.objects.get(id=id).update(**body)
    return '', HTTPStatus.OK


def delete_user(id):
    if not user_id_exists(id):
        return {'error': 'User id not found.'}, HTTPStatus.NOT_FOUND

    devices = Device.objects.filter(id_user=id)

    for device in devices:
        delete_device(id, device.id)

    User.objects.get(id=id).delete()
    return '', HTTPStatus.OK


def add_firebaseToken(id_user):
    body = request.get_json()

    if not body.get('firebaseToken'):
        return {'error': 'The firebaseToken is missing.'}, HTTPStatus.BAD_REQUEST

    if not body.get('id'):
        body["id"] = get_new_id()

    # if "timestamp" in body.keys():
    #     time = body["timestamp"]
    #     body.update({"timestamp": datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')})

    token = FirebaseToken(**body).save()

    id = token.id
    return {'_id': str(id)}, HTTPStatus.CREATED

import os
from datetime import timedelta
from http import HTTPStatus

from flask.json import JSONEncoder
import datetime

from flask import Flask, request
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity
from dotenv import load_dotenv
load_dotenv()

import routes.data_routes
import routes.device_routes
import routes.sensor_routes
import routes.user_routes
import routes.iot_routes
import routes.notifications
import routes.messages_routes


from db import initialize_db
from security.security import (
    authenticate,
    identity,
    is_not_admin,
    is_not_support,
    is_token_stolen
    )

from http_utils.pubsub_client import (PubSubClient, PubSubAuth)


auth = PubSubAuth("secret")

auth.grantSubscribe({
    "token": "secret_token",
    "pattern": "*"
})

auth.grantPublish({
            "token": "36b5fe56debf4309a91817fba1efb743",
            "pattern": "5c19a5a2fcd64e2a9401225b61596b3d.85b4dbc8e1b44cd4b9a2e6aaeb26e851.*"
        })

client = PubSubClient("secret_token", routes.iot_routes.recvData)
import time
time.sleep(1)

client.subscribe("*")


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.date):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = os.environ.get("API_KEY")

# app.config['MONGODB_SETTINGS'] = {
#     'db': os.environ["MONGODB_DATABASE"],
#     'host': os.environ["MONGODB_HOSTNAME"],
#     'port': int(os.environ["MONGODB_PORT"])
# }

app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=36000)

jwt = JWT(app, authenticate, identity)

DB_ADMIN = os.environ.get("DB_ADMIN")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")

import sys
if not DB_ADMIN:
    sys.exit("DB_ADMIN not set!!")
if not DB_PASSWORD:
    sys.exit("DB_PASSWORD not set!!")
if not DB_HOST:
    sys.exit("DB_HOST not set!!")

DB_URL = "mongodb+srv://" + DB_ADMIN + ":" + DB_PASSWORD + "@" + DB_HOST
AUTH_SOURCE = "?authSource=admin"

app.config['MONGODB_SETTINGS'] = [
    {
        'ALIAS': 'user-db-alias',
        'host': DB_URL + "/user" + AUTH_SOURCE
    },
    {
        'ALIAS': 'device-db-alias',
        'host': DB_URL + "/device" + AUTH_SOURCE
    },
    {
        'ALIAS': 'sensor-db-alias',
        'host': DB_URL + "/sensor" + AUTH_SOURCE
    },
    {
        'ALIAS': 'data-db-alias',
        'host': DB_URL + "/data" + AUTH_SOURCE
    },
    {
        'ALIAS': 'firebaseToken-db-alias',
        'host': DB_URL + "/firebaseToken" + AUTH_SOURCE
    },
    {
        'ALIAS': 'messages-db-alias',
        'host': DB_URL + "/messages" + AUTH_SOURCE
    },
]

initialize_db(app)


@app.route('/api/health')
# @jwt_required()
def health_check():
    return {'message': 'Healthy'}, HTTPStatus.OK


@app.route('/api/welcome/<username>')
def welcome(username):
    return routes.user_routes.welcome(username)


@app.route('/api/unsubscribe/<username>')
def unsubscribe(username):
    return routes.user_routes.unsubscribe(username)


# #################################################################################################
# IOT
# #################################################################################################

@app.route('/iot/sync')
def sync():
    return routes.iot_routes.sync()


@app.route('/iot/devices', methods=['POST'])
def iot_device():
    return routes.iot_routes.put_device(auth)


# @app.route('/iot/data', methods=['POST'])
# def iot_data():
#     return routes.iot_routes.put_data()


# #################################################################################################
# USERS
# #################################################################################################


@app.route('/api/users/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    if is_token_stolen(id):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED
    return routes.user_routes.get_user(id)


@app.route('/api/users', methods=['GET'])
@jwt_required()
# @check_admin_credentials
def get_users():
    ret = is_not_admin()
    if ret:
        return ret
    return routes.user_routes.get_users()


@app.route('/api/users/login', methods=['POST'])
def login_user():
    return routes.user_routes.login_user()


@app.route('/api/users', methods=['POST'])
def add_user():
    return routes.user_routes.add_user()


@app.route('/api/users/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    if is_token_stolen(id):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.user_routes.update_user(id)


@app.route('/api/users/forgotPassword', methods=['POST'])
def generate_reset_password_code():
    return routes.user_routes.generate_reset_password_code()


@app.route('/api/users/resetPassword', methods=['POST'])
def reset_password():
    return routes.user_routes.reset_password()


@app.route('/api/users/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    if is_token_stolen(id):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.user_routes.delete_user(id)


@app.route('/api/users/<id_user>/firebaseToken', methods=['POST'])
@jwt_required()
def add_firebaseToken(id_user):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED
    return routes.user_routes.add_firebaseToken(id_user)

# #################################################################################################
# DEVICES
# #################################################################################################


@app.route('/api/users/<id_user>/devices/<id>', methods=['GET'])
@jwt_required()
def get_device(id_user, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED
    return routes.device_routes.get_device(id)


@app.route('/api/devices', methods=['GET'])
@jwt_required()
# @check_admin_credentials
def get_devices():
    ret = is_not_admin()
    if ret:
        return ret
    return routes.device_routes.get_devices()


@app.route('/api/users/<id_user>/devices', methods=['POST'])
@jwt_required()
def add_device(id_user):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED
    return routes.device_routes.add_device(id_user)


@app.route('/api/users/<id_user>/devices', methods=['GET'])
@jwt_required()
def get_user_devices(id_user):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.device_routes.get_user_devices(id_user)


@app.route('/api/users/<id_user>/devices/<id>', methods=['PUT'])
@jwt_required()
def update_device(id_user, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.device_routes.update_device(id_user, id)


@app.route('/api/users/<id_user>/devices/<id>', methods=['DELETE'])
@jwt_required()
def delete_device(id_user, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.device_routes.delete_device(id_user, id)

# #################################################################################################
# SENSORS
# #################################################################################################


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id>', methods=['GET'])
@jwt_required()
def get_sensor(id_user, id_device, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED
    return routes.sensor_routes.get_sensor(id)


@app.route('/api/sensors', methods=['GET'])
@jwt_required()
# @check_admin_credentials
def get_sensors():
    ret = is_not_admin()
    if ret:
        return ret
    return routes.sensor_routes.get_sensors()


@app.route('/api/users/<id_user>/devices/<id_device>/sensors', methods=['POST'])
@jwt_required()
def add_sensor(id_user, id_device):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.sensor_routes.add_sensor(id_user, id_device, request.get_json())


@app.route('/api/users/<id_user>/sensors', methods=['GET'])
@jwt_required()
def get_user_sensors(id_user):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.sensor_routes.get_user_sensors(id_user)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors', methods=['GET'])
@jwt_required()
def get_device_sensors(id_device, id_user):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.sensor_routes.get_device_sensors(id_device, id_user)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id>', methods=['PUT'])
@jwt_required()
def update_sensor(id_user, id_device, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.sensor_routes.update_sensor(id_user, id_device, id)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id>', methods=['DELETE'])
@jwt_required()
def delete_sensor(id_user, id_device, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.sensor_routes.delete_sensor(id_user, id_device, id)


# #################################################################################################
# DATA
# #################################################################################################


@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    ret = is_not_admin()
    if ret:
        return ret
    return routes.data_routes.get_data()


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id_sensor>/data',
           methods=['POST'])
@jwt_required()
def add_data(id_user, id_device, id_sensor):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.data_routes.add_data(id_sensor, request.get_json(), id_user, id_device)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id_sensor>/data',
           methods=['GET'])
@jwt_required()
def get_sensor_data(id_user, id_device, id_sensor):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.data_routes.get_sensor_data(id_user, id_device, id_sensor)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id_sensor>/data/<id>', methods=['DELETE'])
@jwt_required()
def delete_data(id_user, id_device, id_sensor, id):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.data_routes.delete_data(id)


@app.route('/api/users/<id_user>/devices/<id_device>/sensors/<id_sensor>/data/filter', methods=['GET'])
@jwt_required()
def get_filtered_sensor_data(id_user, id_device, id_sensor):
    if is_token_stolen(id_user):
        return {"error": "The authorization token does not belong to you."}, HTTPStatus.UNAUTHORIZED

    return routes.data_routes.get_filtered_sensor_data(id_user, id_device, id_sensor)


# ##############################NOTIFICATIONS##################################

@app.route('/api/users/<id_user>/notify', methods=['POST'])
def send_notifications(id_user):
    return routes.notifications.send_notifications(id_user)

# ##############################  MESSAGES  ##################################

@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    ret = is_not_support()
    if ret:
        return ret
    return routes.messages_routes.get_messages()


@app.route('/api/messages', methods=['POST'])
def add_messages():
    return routes.messages_routes.add_message()


@app.route('/api/messages/<id>', methods=['PUT'])
@jwt_required()
def edit_message(id):
    ret = is_not_support()
    if ret:
        return ret

    return routes.messages_routes.edit_message(id)


@app.route('/api/messages/<id>', methods=['DELETE'])
@jwt_required()
def delete_message(id):
    ret = is_not_support()
    if ret:
        return ret

    return routes.messages_routes.delete_message(id)


@app.route('/api/messages/faq/<id>', methods=['PUT'])
@jwt_required()
def faq_message(id):
    ret = is_not_support()
    if ret:
        return ret

    return routes.messages_routes.faq_message(id)


@app.route('/api/messages/faq', methods=['GET'])
def get_faq_messages():
    return routes.messages_routes.get_faq_messages()


if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=5000, debug=False)
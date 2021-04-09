import re
from http import HTTPStatus
from coolname import generate_slug

from utils import (device_exists, sensor_id_exists, user_email_exists,
                   user_exists, user_id_exists, device_id_exists)

email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
password_regex = r'[A-Za-z0-9@#_*!.,/$%^&+=]{8,}'

# #################################################################################################
# USER
# #################################################################################################


def check_user_post(body):
    name = body.get('name')
    password = body.get('password')
    email = body.get('email')

    if not name:
        return str({'error': 'The username is missing.'}), HTTPStatus.BAD_REQUEST

    if not isinstance(name, str):
        return str({'error': 'The username is invalid.'}), HTTPStatus.BAD_REQUEST

    if user_exists(name):
        return str({'error': 'The username already exists.'}), HTTPStatus.BAD_REQUEST

    if not password:
        return str({'error': 'The password is missing.'}), HTTPStatus.BAD_REQUEST

    if (not isinstance(password, str)) or (not re.fullmatch(password_regex, password)):
        return str({'error': 'The password format is invalid. It must contain at least 8 symbols.'}), HTTPStatus.BAD_REQUEST

    if not email:
        return str({'error': 'The email address is missing.'}), HTTPStatus.BAD_REQUEST

    if (not isinstance(email, str)) or (not re.search(email_regex, email)):
        return str({'error': 'The email format is invalid.'}), HTTPStatus.BAD_REQUEST

    if user_email_exists(email):
        return str({'error': 'The email was already associated with another account.'}), HTTPStatus.BAD_REQUEST

    return None


def check_user_put(body, id):
    if not user_id_exists(id):
        return str({'error': 'The user id does not exist.'}), HTTPStatus.NOT_FOUND

    password = body.get('password')

    # if not password:
    #     return str({'error': 'The password is missing.'}), HTTPStatus.BAD_REQUEST

    if (not isinstance(password, str)) or (not re.fullmatch(password_regex, password)):
        return str({'error': 'The password format is invalid. It must contain at least 8 symbols.'}), HTTPStatus.BAD_REQUEST

    return None

# #################################################################################################
# DEVICE
# #################################################################################################


def check_device_post(body, id_user):
    if body.get("id_user") and id_user != body.get("id_user"):
        return {"error": "The user id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    body["id_user"] = id_user

    if not body.get('name'):
        body['name'] = generate_slug(2)

    if not isinstance(body.get('name'), str):
        return str({'error': 'The device name is invalid.'}), HTTPStatus.BAD_REQUEST

    if not body.get('id_user'):
        return str({'error': 'The user id is missing.'}), HTTPStatus.BAD_REQUEST

    if not user_id_exists(body.get('id_user')):
        return str({'error': 'The user id does not exist.'}), HTTPStatus.NOT_FOUND

    if device_exists(body.get('name'), body.get('id_user')):
        return str({'error': 'The device name already exists for this user.'}), HTTPStatus.BAD_REQUEST

    return None


def check_device_put(body, id, id_user):
    if body.get("id_user") and id_user != body.get("id_user"):
        return {"error": "The user id from the url does not correspond with the one \
            from the payload."}, HTTPStatus.BAD_REQUEST

    body["id_user"] = id_user

    if not device_id_exists(id, id_user):
        return str({'error': 'Device id not found for this user.'}), HTTPStatus.NOT_FOUND

    if device_exists(body.get('name'), id_user):
        return str({'error': 'The device name already exists for this user.'}), HTTPStatus.BAD_REQUEST

    if not set([k for k, _ in body.items()]).issubset(set(['id', 'name', 'description', 'id_user', 'timestamp'])):
        return str({'error': 'One or more of the fields are invalid'}), HTTPStatus.BAD_REQUEST

    return None

# #################################################################################################
# SENSORS
# #################################################################################################

def check_sensor_post(body, id_user, id_device):
    if body.get("id_user") and id_user != body.get("id_user"):
        return {"error": "The user id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if body.get("id_device") and id_device != body.get("id_device"):
        return {"error": "The device id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if not device_id_exists(id_device, id_user):
        return {'error': 'The device id does not exist for this user.'}, HTTPStatus.NOT_FOUND

    body["id_user"] = id_user
    body["id_device"] = id_device

    if not body.get('type'):
        return str({'error': 'The sensor type is missing'}), HTTPStatus.BAD_REQUEST

    if not isinstance(body.get('type'), str):
        return str({'error': 'The type is invalid'}), HTTPStatus.BAD_REQUEST

    if not body.get('measure_unit'):
        return str({'error': 'The measurement unit is missing'}), HTTPStatus.BAD_REQUEST

    if not isinstance(body.get('measure_unit'), str):
        return str({'error': 'The measurement unit is invalid'}), HTTPStatus.BAD_REQUEST

    if not body.get('id_user'):
        return str({'error': 'The user id is missing'}), HTTPStatus.BAD_REQUEST

    if not user_id_exists(body.get('id_user')):
        return str({'error': 'Invalid user id'}), HTTPStatus.BAD_REQUEST

    if not body.get('id_device'):
        return str({'error': 'The device id is missing.'}), HTTPStatus.BAD_REQUEST

    if not device_id_exists(body.get('id_device'), body.get('id_user')):
        return str({'error': 'The device id does not exist for this user.'}), HTTPStatus.NOT_FOUND

    return None


def check_sensor_put(body, id, id_user, id_device):
    if body.get("id_user") and id_user != body.get("id_user"):
            return {"error": "The user id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if body.get("id_device") and id_device != body.get("id_device"):
        return {"error": "The device id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if not user_id_exists(id_user):
        return {'error': "The user id does not exist."}, HTTPStatus.NOT_FOUND

    if not device_id_exists(id_device, id_user):
        return {'error': 'The device id does not exist for this user.'}, HTTPStatus.NOT_FOUND

    body["id_user"] = id_user
    body["id_device"] = id_device

    type = body.get('type')
    measure_unit = body.get('measure_unit')
    id_user = body.get('id_user')
    id_device = body.get('id_device')

    if type:
        return str({'error': 'The sensor type can not be changed'}), HTTPStatus.BAD_REQUEST

    if measure_unit and not isinstance(measure_unit, str):
        return str({'error': 'The measurement unit is invalid'}), HTTPStatus.BAD_REQUEST

    if id_device and not device_id_exists(id_device, id_user):
        return str({'error': 'Invalid device id'}), HTTPStatus.BAD_REQUEST

    if id_user and not user_id_exists(id_user):
        return str({'error': 'Invalid user id'}), HTTPStatus.BAD_REQUEST

    if not set([k for k, _ in body.items()]).issubset(set(['id', 'id_device', 'measure_unit', 'id_user', 'type', 'timestamp'])):
        return str({'error': 'One or more of the fields are invalid'}), HTTPStatus.BAD_REQUEST

    return None


# #################################################################################################
# DATA
# #################################################################################################

def check_data_post(body, id_user, id_device, id_sensor):
    if body.get("id_user") and id_user != body.get("id_user"):
        return {"error": "The user id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if body.get("id_device") and id_device != body.get("id_device"):
        return {"error": "The device id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if body.get("id_sensor") and id_sensor != body.get("id_sensor"):
        return {"error": "The sensor id from the url does not correspond with the one from the payload."}, HTTPStatus.BAD_REQUEST

    if not sensor_id_exists(id_sensor, id_user, id_device):
        return {'error': 'The sensor id does not exist.'}, HTTPStatus.NOT_FOUND

    body["id_user"] = id_user
    body["id_device"] = id_device
    body["id_sensor"] = id_sensor

    if body.get('value') == None:
        return str({'error': 'The value is missing.'}), HTTPStatus.BAD_REQUEST

    return None

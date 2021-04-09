from models.user import User
from models.device import Device
from models.sensor import Sensor
from models.data import Data
from http import HTTPStatus
import uuid
import datetime
import json


def format_timestamp(lst):
    lst_json = list(map(lambda x: json.loads(x.to_json()), lst))
    for i, elem in enumerate(lst):
        # datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        lst_json[i].update({'timestamp': elem.timestamp.strftime('%Y-%m-%d %H:%M:%S')})

    return lst_json


def get_device_apiKey(apiKey):
    devices = Device.objects.filter(apiKey=apiKey)
    if not len(devices) == 0:
        return devices.get(0)
    return None


# #################################################################################################
# USERS
# #################################################################################################

"""
Generate new unique id for the newly-created user/device/sensor/data.
Returns: hex
"""
def get_new_id():
    return uuid.uuid4().hex


"""
Generate new device API key for the newly-created device.
Returns: str
"""
def get_new_device_api_key():
    return uuid.uuid4().hex


"""
Checks if the user with the name <country_name>
exists in the database.
Returns: bool
"""
def user_exists(username):
    return len(User.objects.filter(name=username)) != 0


"""
Checks if the user with the id <_id>
exists in the database.
Returns: bool
"""
def user_id_exists(_id):
    return len(User.objects.filter(id=_id)) != 0


def user_email_exists(email):
    return len(User.objects.filter(email=email)) != 0


"""
Gen the user with the id <_id>.
If the id does not exist in the database, return None.
Returns: User or None
"""
def get_user_by_id(_id):
    if user_id_exists(_id):
        return User.objects.filter(id=_id)[0]
    else:
        return None

# #################################################################################################
# DEVICES
# #################################################################################################

"""
Checks if the user with the name <device_name> and
id <id_user> exists in the database.
Returns: bool
"""
def device_exists(device_name, id_user):
    return len(Device.objects.filter(name=device_name, id_user=id_user)) != 0


"""
Checks if the device with the id <_id>
exists in the database.
Returns: bool
"""
def device_id_exists(_id, id_user):
    return len(Device.objects.filter(id=_id, id_user=id_user)) != 0


"""
Get the device with the id <_id>.
If the id does not exist in the database, return None.
Returns: Device or None
"""
def get_device_by_id(_id, id_user):
    if device_id_exists(_id, id_user):
        return Device.objects.filter(id=_id)[0]
    else:
        return None


# #################################################################################################
# SENSORS
# #################################################################################################

"""
Checks if the device with the id <_id>
exists in the database.
Returns: bool
"""
def sensor_id_exists(_id, id_user, id_device):
    return len(Sensor.objects.filter(id=_id,
                                     id_user=id_user,
                                     id_device=id_device)) != 0


"""
Get the sensor with the id <_id>.
If the id does not exist in the database, return None.
Returns: Sensor or None
"""
def get_sensor_by_id(_id, id_user, id_device):
    if sensor_id_exists(_id, id_user, id_device):
        return Sensor.objects.filter(id=_id,
                                     id_user=id_user,
                                     id_device=id_device)[0]
    else:
        return None


# #################################################################################################
# DATA
# #################################################################################################

"""
Checks if the data with the id <_id>
exists in the database.
Returns: bool
"""
def data_id_exists(_id):
    return len(Data.objects.filter(id=_id)) != 0


"""
Check if the date has a valid format.
Returns: err or None
"""
def check_date(date):
    if date:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
            return None
        except ValueError as err:
            return {'error': 'Invalid time format'}, HTTPStatus.BAD_REQUEST


"""
Check if the data <d> has the given specifications.
Returns: bool
"""
def check_data(d, min_value=None, max_value=None,
               from_date=None, to_date=None):
    if min_value:
        if d.value < float(min_value):
            return False

    if max_value:
        if d.value > float(max_value):
            return False

    timestamp = datetime.datetime.combine(d.timestamp, datetime.datetime.min.time())

    if from_date:
        if timestamp < datetime.datetime.strptime(from_date, "%Y-%m-%d"):
            return False

    if to_date:
        if timestamp > datetime.datetime.strptime(to_date, "%Y-%m-%d"):
            return False

    return True

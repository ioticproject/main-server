import datetime

from db import db
from mongoengine import DateField, StringField, DateTimeField


class Sensor(db.Document):
    id = StringField(primary_key=True)
    id_device = StringField(foreign_key=True)
    id_user = StringField(foreign_key=True)
    type = StringField(required=True, max_length=50)
    measure_unit = StringField(required=True, max_length=50)
    timestamp = DateTimeField(default=datetime.datetime.now())
    # time = StringField(default=datetime.datetime.now().strftime('%a, %d %b %y, %H:%M'))

    meta = {'db_alias': 'sensor-db-alias'}

import datetime

from db import db
from mongoengine import DateField, FloatField, StringField, DateTimeField


class Data(db.Document):
    id = StringField(primary_key=True)
    id_sensor = StringField(foreign_key=True)
    id_device = StringField(foreign_key=True)
    id_user = StringField(foreign_key=True)
    value = FloatField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())

    meta = {'db_alias': 'data-db-alias'}

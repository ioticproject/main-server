import datetime

from db import db
from mongoengine import DateField, StringField, DateTimeField, FloatField


class Device(db.Document):
    id = StringField(primary_key=True)
    name = StringField(required=True, max_length=50)
    description = StringField(required=False, max_length=200)
    id_user = StringField(foreign_key=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    apiKey = StringField()
    min_val = FloatField(required=False, default=-1000)
    max_val = FloatField(required=False, default=1000)

    meta = {'db_alias': 'device-db-alias'}

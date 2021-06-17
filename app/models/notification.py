import datetime

from db import db
from mongoengine import StringField, EmailField, BooleanField, ListField


class Notification(db.Document):
    id = StringField(primary_key=True)
    id_user = StringField(foreign_key=True)
    id_sensor = StringField(foreign_key=True)
    message = StringField(required=True, max_length=500)
    severity = StringField(required=False, default="info")

    meta = {'db_alias': 'notifications-db-alias'}

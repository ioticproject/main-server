import datetime

from db import db
from mongoengine import DateField, StringField, DateTimeField

class Actor(db.Document):
    id = StringField(primary_key=True)
    id_device = StringField(foreign_key=True)
    id_user = StringField(foreign_key=True)
    name = StringField(required=True, max_length=50)
    type = StringField(required=True, max_length=50)
    dataType = StringField(required=True, max_length=25)
    timestamp = DateTimeField(default=datetime.datetime.now())

    meta = {'db_alias': 'actor-db-alias'}

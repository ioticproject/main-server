import datetime

from db import db
from mongoengine import StringField, DateTimeField


class FirebaseToken(db.Document):
    id = StringField(primary_key=True)
    firebaseToken = StringField(required=True, unique=True, max_length=50)
    id_user = StringField(foreign_key=True)
    timestamp = DateTimeField(default=datetime.datetime.now())

    meta = {'db_alias': 'firebaseToken-db-alias'}

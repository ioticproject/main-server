import datetime

from db import db
from mongoengine import StringField, EmailField, BooleanField, ListField


class User(db.Document):
    id = StringField(primary_key=True)
    name = StringField(required=True, unique=True, max_length=50)
    password = StringField(required=True, max_length=50)
    email = EmailField(required=True, unique=True, max_length=50)

    firstName = StringField(required=False, max_length=50, default="Undefined")
    lastName = StringField(required=False, max_length=50, default="Undefined")
    address = StringField(required=False, max_length=50, default="Undefined")
    city = StringField(required=False, max_length=50, default="Undefined")
    state = StringField(required=False, max_length=50, default="Undefined")
    zipCode = StringField(required=False, max_length=50, default="Undefined")
    country = StringField(required=False, max_length=50, default="Undefined")

    confirmed = BooleanField(required=True, default=False)
    resetPasswordCode = StringField(required=False, max_length=50, default="Undefined")

    role = StringField(required=False, max_length=50, default="user")

    meta = {'db_alias': 'user-db-alias'}

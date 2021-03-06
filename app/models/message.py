import datetime

from db import db
from mongoengine import StringField, EmailField, BooleanField, ListField


class Message(db.Document):
    id = StringField(primary_key=True)
    username = StringField(required=True, max_length=50)
    subject = StringField(required=True, max_length=50)
    phone = StringField(required=True, max_length=50)
    text = StringField(required=True, max_length=350) # question
    read = BooleanField(required=False, default=False)
    answer = StringField(required=False, max_length=350)
    faq = BooleanField(required=False, default=False)

    meta = {'db_alias': 'messages-db-alias'}

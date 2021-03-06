import hashlib
import os
from flask_jwt import current_identity
from http import HTTPStatus

from models.user import User


def authenticate(username, password):
    #check for user and return
    if password.startswith('encoded'): 
        return User.objects.filter(name=username, password=password).get(0)
    return User.objects.filter(name=username, password=encode_password(password)).get(0)


#payload is the contents of the jwt token
def identity(payload):
    userid = payload['identity']
    return User.objects.filter(id=userid).get(0)


def encode_password(password):
    return "encoded" + str(hashlib.md5((password + os.getenv("PASSWORD_SECRET")).encode()).hexdigest())


def encode_reset_password_code(resetPasswordCode):
    return str(hashlib.md5((resetPasswordCode + os.getenv("RESET_PASSWORD_SECRET")).encode()).hexdigest())


def check_admin_credentials(func):
    pass
#     def inner():
#         if not current_identity.name == os.getenv("ADMIN_USERNAME") or not current_identity.password == encode_password(os.getenv("ADMIN_PASSWORD")):
#             return {"error": "You must provide the admin credentials in order to access this data."}, HTTPStatus.UNAUTHORIZED

#         return func()
#     return inner

def is_not_admin():
    if not current_identity.role == 'admin':
        return {"error": "You must provide the admin authorization token."}, HTTPStatus.UNAUTHORIZED


def is_not_support():
    if not current_identity.role == 'support':
        return {"error": "You must provide the support authorization token."}, HTTPStatus.UNAUTHORIZED


def is_token_stolen(id_user):
    if not current_identity.id == id_user:
        return True
from __init__ import db
import jwt
import datetime as dt
import os
from time import time

class ResetModel(db.Model):
    __tablename__ = 'reset_password'

    email = db.Column(db.String(), primary_key=True)
    token = db.Column(db.String())
    requested_at = db.Column(db.DateTime(), default=dt.datetime.now())

    def __init__(self, email, token):
        self.email = email
        self.token = token


class LoginModel(db.Model):
    __tablename__ = 'login'

    email = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    phone = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, email, name, phone, password=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

    def set_password(self, password, commit=False):
        self.password = password

        if commit:
            db.session.commit()

    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.email, 'exp': time() + expires},
                           key=os.getenv('SECRET_KEY'))

    @staticmethod
    def verify_reset_token(token):
        try:
            email = jwt.decode(token, key=os.getenv('SECRET_KEY'))['reset_password']
            print(email)
        except Exception as e:
            print(e)
            return
        return LoginModel.query.filter_by(email=email).first()

    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone
            # don't need to send password
            # 'password': self.password
        }

    def __repr__(self):
        return f"<Login {self.name}>"

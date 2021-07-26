from flask import Flask, request, json, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import jwt
from time import time
import os
from __init__ import create_app
from __init__ import db

app = create_app()


from mail_sender import send_email

def send_result(response=None, error='', status=200):
    if response is None: response = {}
    result = json.dumps({'result': response, 'error': error})
    return Response(status=status, mimetype="application/json", response=result)


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

    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.email, 'exp': time() + expires},
                           key=os.getenv('SECRET_KEY_FLASK'))

    @staticmethod
    def verify_reset_token(token):
        try:
            email = jwt.decode(token, key=os.getenv('SECRET_KEY_FLASK'))['reset_password']
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


@app.route('/')
def hello():
    return "Welcome to Privacy Gaurd, are you lost?"


@app.route('/signup', methods=['POST'])
def signup():
    if request.is_json:
        data = request.get_json()
        try:
            new_user = LoginModel(email=data['email'], name=data['name'], phone=data['phone'], password=data['password'])
            db.session.add(new_user)
            db.session.commit()
            return send_result(response='User registered successfully', status=201)
        except KeyError:
            return send_result(error='Email,phone,password are required', status=422)
        except SQLAlchemyError as e:
            return send_result(error="Couldn't register user, possibly because user already exists", status=202)
    else:
        return send_result(error='The request payload is not in JSON format', status=422)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        email = data['email']
        password = data['password']
        result = LoginModel.query.filter_by(email=email, password=password).first()
        if result is None:
            return send_result(error='Incorrect email/password provided', status=401)
        return send_result(result.serialize)
    except KeyError:
        return send_result(error='Email and password are required', status=422)


# Send password reset email
@app.route('/recovery', methods=['POST'])
def reset():
    email = request.form.get('email')    
    user = LoginModel.query.filter_by(email=email).first()
    if user:
        send_email(user)
        return send_result(response='Request processed successfully', status=201)

    return send_result(error='No account found with that email', status=401)


@app.route('/recovery_verified/<token>', methods=['GET', 'POST'])
def reset_verified(token):

    user = LoginModel.verify_reset_token(token)
    if not user:
        print('no user found')
        return render_template('invalid_session.html')

    password = request.form.get('password')
    if password:
        user.set_password(password, commit=True)

        return render_template('reset_success.html')

    return render_template('reset_verified.html')


if __name__ == '__main__':
    app.run()

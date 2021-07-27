from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os

basedir = os.path.abspath(os.path.dirname(__file__))

os.environ['SECRET_KEY'] = 'privacy-guard'

class Configuration:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql://root@127.0.0.1/privacy_guard"
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "43188a@gmail.com"
    MAIL_PASSWORD = "03108160246"
    SECRET_KEY = os.getenv('SECRET_KEY')


db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app():
    # Rule no. 1 never use "localhost" always use "127.0.0.1" to ensure server usese IPV4 addressing
    app = Flask(__name__)
    app.config.from_object(Configuration)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    return app


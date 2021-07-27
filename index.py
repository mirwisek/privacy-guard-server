from flask import request, json, Response, render_template
from sqlalchemy import exc
from __init__ import create_app
from __init__ import db
from models import LoginModel, ResetModel
import socket

app = create_app()

from mail_sender import send_email

def send_result(response=None, error='', status=200):
    if response is None: response = {}
    result = json.dumps({'result': response, 'error': error})
    return Response(status=status, mimetype="application/json", response=result)

@app.route('/')
def hello():
    return "Welcome to Privacy Gaurd, are you lost?"


@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    try:
        new_user = LoginModel(email=data['email'], name=data['name'], phone=data['phone'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return send_result(response='User registered successfully', status=201)
    except KeyError:
        # Send response as String and not as default dict, for consistensy at android side
        return send_result(error='Email,phone,password are required', response='', status=422)
    except exc.IntegrityError as e:
        db.session.rollback()
        return send_result(error="Couldn't register user, possibly because user already exists", response='', status=202)    
    # return send_result(error='The request payload is not in JSON format', status=422)


@app.route('/login', methods=['POST'])
def login():
    data = request.form
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
    data = request.form
    email = data['email'] 
    user = LoginModel.query.filter_by(email=email).first()
    if user:
        token = user.get_reset_token()
        reset_entry = ResetModel(email, token)
        # update entry to avoid duplicate primary key error
        db.session.merge(reset_entry)
        send_email(user, token)
        db.session.commit()
        return send_result(response='Request processed successfully', status=201)

    return send_result(error='No account found with that email', status=401)


@app.route('/recovery_verified/<token>', methods=['GET', 'POST'])
def reset_verified(token):

    user = LoginModel.verify_reset_token(token)
    if not user:
        return render_template('invalid_session.html')

     # Check if a reset_password table has a token against this email, otherwise password has already been reset
    reset_entry = ResetModel.query.filter_by(token=token).first()
    if not reset_entry:
        return render_template('invalid_session.html')

    password = request.form.get('password')
    if password:
        user.set_password(password, commit=True)
        # make sure the link doesn't work after reseting password by removing the token entry from reset_password table
        ResetModel.query.filter(ResetModel.token == token).delete()
        db.session.commit()
        return render_template('reset_success.html')

    return render_template('reset_verified.html')


if __name__ == '__main__':
    # Print ip address of PC
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print('Your IP Address for this PC is: {}'.format(s.getsockname()[0]))
    s.close()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
    

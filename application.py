from random import randint
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import db
import config
import requests
import json
import os 


application = Flask(__name__)
application.secret_key = os.environ['APP_SECRET_KEY']


# Instantiate Mail/ OTP for registration
application.config['MAIL_SERVER']=os.environ['MAIL_SERVER']
application.config['MAIL_PORT']=os.environ['MAIL_USERNAME']
application.config['MAIL_USERNAME']=os.environ['MAIL_PASSWORD']
application.config['MAIL_PASSWORD']=os.environ['MAIL_PORT']
application.config['MAIL_USE_TLS']=os.environ['MAIL_USE_SSL']
application.config['MAIL_USE_SSL']=os.environ['MAIL_USE_TLS']

url_serializer = URLSafeTimedSerializer(config.URLSAFE_KEY)
otp_generated = randint(1000,9999)
mail = Mail(application)



@application.route('/')
def index():
    return render_template('index.html')

@application.route('/home')
def home():
    return render_template('index.html')

@application.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = db.generate_password_hash(password)

        session["reg_success"] = False
        session['token'] = url_serializer.dumps([username, hashed_password], salt='email-confirm')
        
        msg = Message('Valo360 OTP Confirmation', sender=('Valo360 Support','support@valo360.in'), recipients=[username])
        msg.body = 'Your OTP is {}'.format(otp_generated)
        assert msg.sender == "Valo360 Support <support@valo360.in>"
        mail.send(msg)
        
        return render_template('verification.html')
    
    return render_template('registration.html')

# @application.route('/confirm_email/<token>')
# def confirm_email(token):
#     try:
#         username = s.loads(token, salt='email-confirm', max_age=3600)
#     except SignatureExpired:
#         return '<h1>The token is expired!</h1>'
#     return create_user(username)

@application.route('/verification',  methods=['POST'])
def verification():
    otp_user = request.form['otp']

    try:
        if otp_generated == int(otp_user):
            username, hashed_password = url_serializer.loads(session['token'], salt='email-confirm', max_age=1800)
            db.create_user(username, hashed_password)
            session["reg_success"] = True
            return redirect(url_for('login'))
        
    except ValueError:
        return render_template('verification.html', msg='Invalid')
    
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    
    return render_template('verification.html', msg='not verified' )

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return db.login_user(username, password)
    
    return render_template('login.html')

@application.route('/contact')
def contact():
    return render_template('contact.html')

@application.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f'Welcome {session["username"]}! This is your dashboard.'
    return redirect(url_for('login'))

@application.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@application.route("/weapons", methods=['GET', 'POST'])
def weapons():
    weapon_request = requests.get("https://valorant-api.com/v1/weapons")
    json_data = json.loads(weapon_request.content)
    if request.method == "GET":
        return render_template(
        "weapons.html",
        title="Weapon",
        data = json_data
        )
    if request.method == "POST":
        form_data = request.form.getlist("weapon_list_checkbox")
        db.insert_weapon(form_data)
        return redirect(url_for("weapons"))
    

if __name__ == '__main__':
    application.run(debug=True)

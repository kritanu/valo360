from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import config
from models import WeaponList
import uuid
from dataclasses import asdict

# Connect to MongoDB
client = MongoClient(config.DATABASE_URI)
db = client[config.DATABASE_NAME]
weapons_collection = db[config.DATABASE_WEAPONS]
users_collection = db[config.DATABASE_USERS]

# Check if username already exists
def create_user(username, hashed_password):
        if users_collection.find_one({'username': username}):
            return 'Username already exists!'

        # Insert new user into database
        users_collection.insert_one({'username': username, 'password': hashed_password, 'confirmed': 0})
        return redirect(url_for('verification'))

def confirm_user(username):
        users_collection.update_one({"username":username},{"$set":{'confirmed':1}})
        return redirect(url_for('login'))


def login_user(username, password):
        # Check if username exists in database
        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))

        return 'Invalid username/password combination'


def insert_weapon(form_data):
        weapon_list = WeaponList(
            _id=uuid.uuid4().hex,
            wp_list = list(form_data)
        )
        weapons_collection.insert_one(asdict(weapon_list))
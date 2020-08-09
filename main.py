from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from logging import Logger
from datetime import datetime
import json

#TelegramAPI
TOKEN = '1261141644:AAFQ3R_EdT5GYVLvADFt9mPT45JzgI0STEE'
TELEGRAM_API = 'https://api.telegram.org/bot{}/'.format(TOKEN)

#Starting Flask
app = Flask(__name__)

#SQL Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysql://vireak:password@localhost/TODO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

#SQL Database Models
class User(db.Model):
    __tablename__ = 'USER'
    user_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger)
    user_name = db.Column(db.String)
    date_created = db.Column(db.DateTime)

class Todo(db.Model):
    #__tablename__ = 'TODO'
    id = db.Column(db.SmallInteger, primary_key=True)
    user_id = db.Column(db.SmallInteger)
    post_title = db.Column(db.String(64))
    post_desc = db.Column(db.String(255))
    date_created = db.Column(db.DateTime)

#Flask APP route
@app.route('/')
def home():
    return 'hello world'

#@app.route('/setWebhook')
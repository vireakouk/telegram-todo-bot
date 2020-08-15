from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
import telegram
from credentials import telegram_token, telegram_api
from logging import Logger
from datetime import datetime
import json
import requests

#TelegramAPI
TOKEN = telegram_token
TELEGRAM_API = telegram_api
bot = telegram.Bot(token=TOKEN)
print(bot)

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
@app.route('/', methods=['POST', 'GET'])
def respond():
    app.logger.info('respond')
    if request.method == 'POST':
        # retrieve the message json and then automatically transform it to dictionary
        update = request.get_json(force=True)
        print(update)
        #retrieve chat_id
        chat_id = update['message']['chat']['id']
        print(chat_id)

        if 'message' in update:
            message_id = update['message']['message_id']
            text = update['message']['text']
            print(text)
            if text == '/start':
                bot.sendChatAction(chat_id=chat_id, action='typing')
                bot.sendMessage(chat_id=chat_id, text='Welcome to My Telegram Todo List', parse_mode='html')

    # if request.is_json:
    #     print("is json")
    #     data = request.get_json()
    #     print("type of data {}".format(type(data))) # type dict
    #     print("data as string {}".format(json.dumps(data)))
    #     print ("keys {}".format(json.dumps(data.keys())))
        return 'webhook works'
    else:
        return 'ok'

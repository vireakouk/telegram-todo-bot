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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vireak:password@localhost/TODO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
session = db.session

#SQL Database Models
class User(db.Model):
    __tablename__ = 'USER'
    user_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger)
    todo_list = db.relationship('Todo', backref=db.backref('owner', lazy=True))
    user_name = db.Column(db.String)
    state = db.Column(db.SmallInteger, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Todo(db.Model):
    __tablename__ = 'TODO'
    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('USER.user_id'))
    post_title = db.Column(db.String(64))
    post_desc = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

#build todo_keyboard with 3 buttons
todo_buttons = [
    [telegram.InlineKeyboardButton(text='New Todo', callback_data='1')],
    [telegram.InlineKeyboardButton(text='Show Todo', callback_data='2'),
    telegram.InlineKeyboardButton(text='Delete Todo', callback_data='3')]
]
todo_keyboard = telegram.InlineKeyboardMarkup(todo_buttons)

#Flask APP route
@app.route('/', methods=['POST', 'GET'])
def respond():
    app.logger.info('respond')
    if request.method == 'POST':
        # retrieve the message json and then automatically transform it to dictionary
        update = request.get_json()
        print(update)


        if 'message' in update:
            chat_id = update['message']['chat']['id']
            first_name = update['message']['chat']['first_name'] 
            message_id = update['message']['message_id']
            text = update['message']['text']
            current_user = User.query.filter_by(telegram_id=chat_id).first()

            #if user doesn't exist, add that user into database
            if session.query(User).filter_by(telegram_id=chat_id).first() is None:
                session.add(User(telegram_id=chat_id, user_name=first_name))
                session.commit()
            
            if text == '/start':
                bot.sendChatAction(chat_id=chat_id, action='typing')
                bot.sendMessage(chat_id=chat_id, text='Welcome to My Telegram Todo List', parse_mode='html', reply_markup=todo_keyboard)
            
            elif current_user.state == 1:
                # session.add(Todo(user_id=current_user.user_id, post_title=text))
                session.query(User).filter_by(telegram_id=chat_id).update({'state': 11})
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Please Enter Todo description:', parse_mode='html')

            elif current_user.state == 11:
            #     session.query(Todo).filter_by(user_id=User.user_id).update({'post_description': text})
                session.query(User).filter_by(telegram_id=chat_id).update({'state': 0})
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Your Todo list is updated.', parse_mode='html')
            
        if 'callback_query' in update:
            chat_id = update['callback_query']['message']['chat']['id']
            callback_id = int(update['callback_query']['data'])

            if callback_id == 1:
                session.query(User).filter_by(telegram_id=chat_id).update({'state': callback_id})
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Please Enter Todo title:', parse_mode='html')
            if callback_id == 2:
                pass
            if callback_id ==3:
                pass


        return 'webhook works'
    else:
        return 'methods not allowed.'

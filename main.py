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
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    todo_list = db.relationship('Todo', backref='owner', lazy=True)
    username = db.Column(db.String(64), unique=True, nullable=True)
    state = db.Column(db.SmallInteger, default=0)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.user_id}', '{self.username}', '{self.telegram_id}', '{self.todo_list}')"

class Todo(db.Model):
    __tablename__ = 'TODO'
    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('USER.telegram_id'), nullable=False)
    post_title = db.Column(db.String(64))
    post_desc = db.Column(db.String(255))
    order_id = db.Column(db.SmallInteger, nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Todo('{self.id}', '{self.owner_id}', '{self.post_title}', '{self.post_desc}')"

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
        show_todo = 'Here is your todo list:\n'
        i = 0

        if 'message' in update:
            chat_id = update['message']['chat']['id']
            username = update['message']['chat']['username'] 
            message_id = update['message']['message_id']
            text = update['message']['text']

            current_user = User.query.filter_by(telegram_id=chat_id).first()
            print(current_user)
            current_todo = Todo.query.filter_by(owner_id=chat_id).order_by((Todo.date_created.desc())).first()
            print(current_todo)

            
            
            #if user doesn't exist, add that user into database
            if current_user is None:
                session.add(User(telegram_id=chat_id, username=username))
                session.commit()
            
            
            if text == '/start':
                # delete incomplete todo session when user enter Todo category and then failed to enter descriptions. This is flagged by post_desc=None 
                Todo.query.filter_by(owner_id=chat_id).filter_by(post_desc=None).delete()
                current_user.state = 0
                session.commit()
                bot.sendChatAction(chat_id=chat_id, action='typing')
                bot.sendMessage(chat_id=chat_id, text='Welcome to My Telegram Todo List:', parse_mode='html', reply_markup=todo_keyboard)
            
            elif current_user.state == 1 and text != '/start':
                session.add(Todo(owner=current_user, post_title=text))
                current_user.state = 11
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Please Enter Todo description:', parse_mode='html')

            elif current_user.state == 11:
                current_todo.post_desc = text
                current_user.state = 0
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Your todo list is updated.\nThanks for using this program!', parse_mode='html')
                
                for row in current_user.todo_list:
                    i += 1
                    row.order_id = i
                    show_todo = show_todo + str(row.order_id) + '. ' + str(row.post_title) + ': ' + str(row.post_desc) + '\n'
                show_todo = 'You don\'t have anything to do yet. Click /start to get going' if i==0 else show_todo
                bot.sendMessage(chat_id=chat_id, text=show_todo, parse_mode='html', reply_markup=todo_keyboard)

            elif current_user.state == 3:
                if current_user.todo_list:
                    try:
                        delete_id = int(text)
                        if Todo.query.filter_by(owner_id=chat_id).filter_by(order_id=delete_id).first() is None:
                            bot.sendMessage(chat_id=chat_id, text='There is no such item in your todo list. Please re-enter a valid ID:', parse_mode='html')
                            for row in current_user.todo_list:
                                i += 1
                                row.order_id = i
                                show_todo = show_todo + str(row.order_id) + '. ' + str(row.post_title) + ': ' + str(row.post_desc) + '\n'
                            bot.sendMessage(chat_id=chat_id, text=show_todo, parse_mode='html')
                        else:
                            Todo.query.filter_by(owner_id=chat_id).filter_by(order_id=delete_id).delete()
                            current_user.state = 0
                            session.commit()
                            bot.sendMessage(chat_id=chat_id, text='Your todo list is updated.\nThanks for using this program! Click /start to continue.', parse_mode='html')
                    except ValueError:
                        current_user.state = 0
                        session.commit()
                        bot.sendMessage(chat_id=chat_id, text='Unknown command. Your session is reset. Click /start to get going.', parse_mode='html')
                           
                else:
                    current_user.state = 0
                    session.commit()
                    bot.sendMessage(chat_id=chat_id, text='Unknown command.\nPlease click on what you want to do:', parse_mode='html', reply_markup=todo_keyboard)
            else:
                current_user.state = 0
                session.commit()
                bot.sendMessage(chat_id=chat_id, text='Unknown command.\nPlease click on what you want to do:', parse_mode='html', reply_markup=todo_keyboard)
            
            
        if 'callback_query' in update:
            callback_id = int(update['callback_query']['data'])
            chat_id = update['callback_query']['message']['chat']['id']
            Todo.query.filter_by(owner_id=chat_id).filter_by(post_desc=None).delete()
            try:
                current_user = User.query.filter_by(telegram_id=chat_id).first()
                for row in current_user.todo_list:
                    i += 1
                    row.order_id = i
                    show_todo = show_todo + str(row.order_id) + '. ' + str(row.post_title) + ': ' + str(row.post_desc) + '\n'
                show_todo = 'You don\'t have anything to do yet. Click /start to get going' if i==0 else show_todo
                session.commit()

                if callback_id == 1:
                    current_user.state = 1
                    session.commit()
                    bot.sendMessage(chat_id=chat_id, text='Please Enter Todo category:', parse_mode='html')
                if callback_id == 2:
                    current_user.state = 2
                    session.commit()
                    bot.sendMessage(chat_id=chat_id, text=show_todo, parse_mode='html')
                    if i !=0: bot.sendMessage(chat_id=chat_id, text='What else do you want to do?', parse_mode='html', reply_markup=todo_keyboard)
                if callback_id == 3:
                    current_user.state = 3
                    session.commit()
                    bot.sendMessage(chat_id=chat_id, text=show_todo, parse_mode='html')
                    if i !=0: bot.sendMessage(chat_id=chat_id, text='Please Enter the Todo ID you want to delete:', parse_mode='html')
            except NotImplementedError:
                bot.sendMessage(chat_id=chat_id, text='Click /start to get going!', parse_mode='html')                       

        return 'webhook works'
    else:
        return 'methods not allowed.'

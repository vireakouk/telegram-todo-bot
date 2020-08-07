from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from logging import Logger
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysql://root@localhost/todos'
db = SQLAlchemy(app)


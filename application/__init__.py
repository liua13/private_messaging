import os
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database, drop_database

from config import Config
from flask_restx import Api

app = Flask(__name__)
app.config.from_object(Config)

sess = Session()

db = SQLAlchemy(app)
db.init_app(app)

sess.init_app(app)
from flask_socketio import SocketIO
socketio = SocketIO()
socketio.init_app(app, manage_session=False)

DB_URL = os.environ.get("SQLALCHEMY_DATABASE_URI")
# if database_exists(DB_URL):
#     print('DELETING DATABASE.')
#     drop_database(DB_URL)
if not database_exists(DB_URL):
    print('CREATING DATABASE')
    create_database(DB_URL)

from application.models import User

print("CREATING TABLES")
db.create_all()

from application import routes
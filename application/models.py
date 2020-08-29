import flask, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects import postgresql
from application import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.Text)

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)

class ChatRoom(db.Model):
    __tablename__ = 'chatrooms'
    id = db.Column(db.Integer, primary_key=True)
    senderID = db.Column(db.Integer)  # matches id of a `User`
    recipientID = db.Column(db.Integer) # ID of who the message is sent to

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chatID = db.Column(db.Integer) # matches id of a `ChatRoom`
    senderID = db.Column(db.Integer)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message = db.Column(db.Text)
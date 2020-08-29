from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, json
import os, datetime
from flask_socketio import send, emit, join_room, leave_room
from application import app, db, socketio
from application.models import User, ChatRoom, Message
from application.forms import LoginForm, RegisterForm, SendMessageForm
from werkzeug.datastructures import MultiDict
            
@app.route("/register", methods=["GET", "POST"])
def register():

    if session.get("user"):
        return redirect(url_for("index"))

    registerForm = RegisterForm()

    if request.method == "GET":
        return render_template("register.html", registerForm=registerForm)
    elif request.method == "POST":
        if registerForm.validate_on_submit():
            id = User.query.count() + 1
            email = registerForm.email.data 
            password = registerForm.password.data
            firstName = registerForm.firstName.data
            lastName = registerForm.lastName.data
            
            user = User(id=id, email=email, firstName=firstName, lastName=lastName)
            user.setPassword(password)
            db.session.add(user)
            db.session.commit()

            session["user"] = {"id": id, "email": email, "firstName": firstName, "lastName": lastName}
            
            flash("You have successfully registered", "success")
            return redirect(url_for("index"))
        else:
            return render_template("register.html", registerForm=registerForm)

    flash("There was some trouble registering you. Please try again.", "danger")
    return render_template("register.html", registerForm=registerForm)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("index"))
    
    loginForm = LoginForm()

    if request.method == "GET":
        return render_template("login.html", loginForm=loginForm)
    elif request.method == "POST":
        if loginForm.validate_on_submit():
            email = loginForm.email.data
            password = loginForm.password.data
            user = db.session.query(User).filter(User.email==email).first()
            if user and user.checkPassword(password):
                id = user.id
                firstName = user.firstName
                lastName = user.lastName
                session["user"] = {"id": id, "email": email, "firstName": firstName, "lastName": lastName}

                flash(f"{user.firstName}, you have successfully logged in", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username / password.", "danger")
        return render_template("login.html", loginForm=loginForm)

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("currentChat", None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    
    form = SendMessageForm()
    return render_template("index.html", form=form)

@socketio.on("message")
def message(form):
    form = SendMessageForm(formdata=MultiDict(form), meta={'csrf': False})

    if not form.validate():
        print(form.recipientID.errors + form.message.errors)
        # socketio.emit("sendMessageError", {"recipientEmail": form.recipientEmail.errors})
    else:
        datetime = form.datetime.data
        chatID = form.chatID.data
        recipientID = form.recipientID.data
        message = form.message.data
        # socketio.emit("sendMessageError", {"recipientEmail": ""})

        id = Message.query.count() + 1
        newMessage = Message(id=id, datetime=datetime, chatID=chatID, senderID=session["user"]["id"], message=message)
        db.session.add(newMessage)
        db.session.commit()

        socketio.emit("sentMessage", {"recipientID": recipientID, "senderID": session.get("user").get("id"), "message": message, "datetime": datetime}, room=session.get("user").get("id"))

        user = db.session.query(User).filter((User.id == session["user"]["id"])).first()

        socketio.emit("receivedMessage", {"chatID": chatID, "recipientID": recipientID, "senderID": session.get("user").get("id"), "message": message, "datetime": datetime, "firstName": user.firstName}, room=recipientID)

@socketio.on("userConnected")
def userConnected():
    join_room(session.get("user").get("id"))
    chatRooms = db.session.query(ChatRoom).filter((ChatRoom.senderID == session.get("user").get("id")) | (ChatRoom.recipientID == session.get("user").get("id"))).all()
    allChats = []
    for chatRoom in chatRooms:
        if chatRoom.senderID == session.get("user").get("id"):
            userID = chatRoom.recipientID # other user
        else:
            userID = chatRoom.senderID

        recipientUser = db.session.query(User).filter((User.id == userID)).first()
        if recipientUser:
            allChats.append({"chatID": chatRoom.id, "userID": userID, "firstName": recipientUser.firstName})
    socketio.emit("chatRooms", allChats, room=session.get("user").get("id"))

@socketio.on("changeChat")
def changeChat(userID, chatID):
    session["currentChat"] = userID
    messages = db.session.query(Message).filter((Message.chatID == chatID)).all()
    allMessages = []
    for message in messages:
        messageType = "receivedMessage"
        if session["user"]["id"] == message.senderID:
            messageType = "sentMessage"
        allMessages.append({"chatID": chatID, "messageType": messageType, "datetime": json.dumps(message.datetime, default=stringifyDateTime), "message": message.message})
    socketio.emit("displayAllMessages", allMessages, room=session["user"]["id"])


def stringifyDateTime(dateTimeObject):
    if isinstance(dateTimeObject, datetime.datetime):
        return dateTimeObject.__str__()

@socketio.on("receivedMessage")
def receivedMessage(data):
    if data["senderID"] == session.get("currentChat"):
        socketio.emit("displayReceivedMessage", data, room=data["recipientID"])
    else:
        socketio.emit("displayNotification", data, room=data["recipientID"])
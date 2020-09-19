from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import PasswordInput

from application import db
from application.models import User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired()], widget=PasswordInput(hide_value=False))
    rememberMe = BooleanField("Remember me")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired(), Length(min=6)], widget=PasswordInput(hide_value=False))
    passwordConfirm = StringField("Confirm Password", validators=[DataRequired(), Length(min=6), EqualTo("password")], widget=PasswordInput(hide_value=False))
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField("Register")

    # automatically validates on the `email` field because it's called `validate_email`
    def validate_email(self, email):
        user = db.session.query(User).filter(User.email == email.data).first()
        if user:
            raise ValidationError("An account under this email address has already been created.")

class SendMessageForm(FlaskForm):
    datetime = StringField("Date", validators=[DataRequired()])
    chatID = IntegerField("ChatID", validators=[DataRequired()])
    recipientID = IntegerField("To:", render_kw={"placeholder": "No recipients"})
    message = TextAreaField("Message", validators=[DataRequired()], render_kw={"placeholder": "Message"})
    submit = SubmitField("Send")

    def validate_recipientID(self, recipientID):
        user = db.session.query(User).filter(User.id == recipientID.data).first()
        if not user:
            raise ValidationError("No such account exists.")
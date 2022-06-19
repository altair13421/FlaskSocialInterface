from flask import Flask
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from app.models import Users

# Forms Here
class LoginForm(FlaskForm):
    username = StringField('Username Or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Submit")
    pass

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_re = PasswordField('Re enter Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please Use a Different Username.')
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please Use a Different Email')

class ProfileForm(FlaskForm):
    about_me = StringField('About me')
    avatar = FileField('image', validators=[FileAllowed(['jpg', 'png'], 'Images Only')])
    submit = SubmitField("Update")

class EntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = StringField('Body')
    submit = SubmitField("Submit")
    pass

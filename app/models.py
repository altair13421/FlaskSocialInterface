from datetime import datetime
from enum import unique
from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .configs import image_dir
import requests, os
from hashlib import md5

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    about_me = db.Column(db.String(128), index=True)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    avatar = db.Column(db.String(256), index=True)
    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    @login.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    def set_password(self, passwordtoset):
        self.password = generate_password_hash(passwordtoset)
    
    def check_password(self, passwordtocheck):
        return check_password_hash(self.password, passwordtocheck)

    def show_avatar(self):
        return self.avatar

    def __repr__(self) -> str:
        return f'<User {self.username}>'

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_body = db.Column(db.String(256), index=True)
    post_title = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self) -> str:
        return f'<Post {self.post_title}>'
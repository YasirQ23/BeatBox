from uuid import uuid4
from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import jwt
from app import db, login


followers = db.Table('followers',
                     db.Column('follower_id', db.String(
                         40), db.ForeignKey('user.id')),
                     db.Column('followed_id', db.String(40), db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.String(40), primary_key=True)
    username_id = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    api_token = db.Column(db.String)
    bio = db.Column(db.String(255))
    grid = db.relationship('Grid', backref='user', lazy=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    likes = db.relationship('Likes', backref='liker', lazy='dynamic')
    comments = db.relationship(
        'Comment', backref='comment_author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username, email, password, first_name, last_name):
        self.username_id = username.lower()
        self.username = username
        self.email = email.lower()
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.id = str(uuid4())
        self.password = generate_password_hash(password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(userid):
    return User.query.get(userid)


class Grid(db.Model, UserMixin):
    id = db.Column(db.String(40), primary_key=True)
    artist = db.Column(db.String(100))
    track = db.Column(db.String(100))
    track_img = db.Column(db.String(225))
    grid_position = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.String(40), db.ForeignKey(
        'user.id'), nullable=False)

    def __init__(self, user_id, grid_position):
        self.id = str(uuid4())
        self.track_img = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRZeOUhcj7Et-Xz6R0q4qQy472fzV9HvSplg&usqp=CAU'
        self.user_id = user_id
        self.grid_position = grid_position


class Post(db.Model, UserMixin):
    id = db.Column(db.String(40), primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    location_id = db.Column(db.String(40), nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(40), db.ForeignKey(
        'user.id'), nullable=False)
    liked = db.relationship('Likes', backref='Post', lazy='dynamic')
    comment = db.relationship('Comment', backref='post_owner', lazy='dynamic')

    def __init__(self, user_id, body, location_id):
        self.id = str(uuid4())
        self.user_id = user_id
        self.body = body
        self.location_id = location_id
        self.likes = 0
        self.comments = 0

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Likes(db.Model, UserMixin):
    id = db.Column(db.String(40), primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.String(40), db.ForeignKey(
        'post.id'), nullable=False)
    user_id = db.Column(db.String(40), db.ForeignKey(
        'user.id'), nullable=False)

    def __init__(self, user_id, post_id):
        self.id = str(uuid4())
        self.user_id = user_id
        self.post_id = post_id


class Comment(db.Model, UserMixin):
    id = db.Column(db.String(40), primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.String(40), db.ForeignKey(
        'post.id'), nullable=False)
    user_id = db.Column(db.String(40), db.ForeignKey(
        'user.id'), nullable=False)

    def __init__(self, body, user_id, post_id):
        self.id = str(uuid4())
        self.user_id = user_id
        self.body = body
        self.post_id = post_id

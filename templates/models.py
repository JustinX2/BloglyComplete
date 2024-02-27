"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, default='https://www.freeiconspng.com/img/17660')

    def __repr__(self):
        return f'<User {self.id}: {self.first_name} {self.last_name}>'
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('posts'))
    
    def __repr__(self):
        return f'<Post {self.id}: {self.title}>'

class Tag(db.Model):
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False, unique=True)

    posts=db.relationship('Post', secondary='posts_tags', backref='tags')

class PostTag(db.Model):
    __tablename__='posts_tags'
    post_id=db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)


def connect_db(app):
    db.app = app
    db.init_app(app)

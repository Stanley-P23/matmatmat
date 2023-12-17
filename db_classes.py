from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from flask import Flask
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
os.environ.get('FLASK_KEY')


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQL_URI')
db = SQLAlchemy()
db.init_app(app)

# CONFIGURE TABLES




class Infos(db.Model):
    __tablename__ = "infos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)



    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")




class Series(db.Model):
    __tablename__ = "exercises_serieses"

    id = db.Column(db.Integer, primary_key=True)
    session_no = db.Column(db.Integer(), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(40), nullable=False)
    finish_date = db.Column(db.String(40), nullable=False)
    exercises = relationship("Exercise", back_populates="series")
    answers = relationship("Answer", back_populates="series")


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    value1 = db.Column(db.Text, nullable=False)
    value2 = db.Column(db.Text, nullable=False)
    value3 = db.Column(db.Text, nullable=False)
    value4 = db.Column(db.Text, nullable=False)
    correct = db.Column(db.String(1), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    series_id = db.Column(db.Integer, db.ForeignKey("exercises_serieses.id"),  nullable=False)
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    series = relationship("Series", back_populates="exercises")
    answers = relationship("Answer", back_populates="exercise")

class User(UserMixin, db.Model):

    __tablename__ = "users"


    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    answers = relationship("Answer", back_populates="user")

class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)



    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="answers")


    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    exercise = relationship("Exercise", back_populates="answers")


    series_id = db.Column(db.Integer, db.ForeignKey("exercises_serieses.id"), nullable=False)
    series = relationship("Series", back_populates="answers")

    answer = db.Column(db.String(1), nullable=False)
    point = db.Column(db.Boolean, nullable=False)




class Comment(db.Model):
    __tablename__ = "comments"


    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="comments")

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    post = relationship("BlogPost", back_populates="comments")







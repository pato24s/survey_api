from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from passlib.apps import custom_app_context as pwd_context
from flask_migrate import Migrate

from sqlalchemy.orm import relationship

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/surveys_api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)


selected_answers = Table('selected_answers', db.metadata, Column('user_id', Integer, ForeignKey('users.id')),
                         Column('answer_id', Integer, ForeignKey('answers.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(32))
    password = db.Column(db.String(128))
    surveys = relationship("Survey")
    questions = relationship("Question")
    selected_answers = relationship("Answer", secondary=selected_answers)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    tags = db.Column(db.String(128))
    title = db.Column(db.String(128))
    expiration_date = db.Column(db.DateTime)
    questions = relationship("Question")
    creator_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, tags, title, expiration_date):
        self.tags = tags
        self.title = title
        self.expiration_date = expiration_date


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    answers = relationship("Answer")
    survey_id = Column(Integer, ForeignKey('surveys.id'))
    creator_id = Column(Integer, ForeignKey('users.id'))


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    question_id = Column(Integer, ForeignKey('questions.id'))


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/users', methods=['POST'])
def new_user():
    name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if name is None or email is None or password is None:
        response = jsonify("Missing arguments.")
        response.status_code = 400
        return response
    if User.query.filter_by(email=email).first() is not None:
        response = jsonify("Email is invalid or already taken.")
        response.status_code = 400
        return response
    hashed_password = pwd_context.encrypt(password)
    user = User(name, email, hashed_password)
    db.session.add(user)
    db.session.commit()
    response = jsonify("User correctly created.")
    return response


if __name__ == '__main__':
    app.run()

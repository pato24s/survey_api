from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
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
auth = HTTPBasicAuth()

selected_answers = Table('selected_answers', db.metadata, Column('user_id', Integer, ForeignKey('users.id')),
                         Column('answer_id', Integer, ForeignKey('answers.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(32))
    password = db.Column(db.String(128))
    surveys = relationship("Survey", backref='creator')
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


@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return True

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


@app.route('/api/surveys', methods=['POST'])
@auth.login_required
def new_survey():
    tags = request.form.get('tags') or None
    title = request.form.get('title')
    expiration_date = request.form.get('expiration_date') or None
    if title is None:
        response = jsonify("Cant create survey without title.")
        response.status_code = 400
        return response
    if expiration_date is not None:
        expiration_date = datetime.strptime(expiration_date, '%d/%m/%Y')
    email = request.authorization.username
    creator = User.query.filter_by(email=email).first()
    survey = Survey(tags=tags, title=title, expiration_date=expiration_date, creator=creator)
    db.session.add(survey)
    db.session.commit()
    response = jsonify("Survey correctly created.")
    return response


if __name__ == '__main__':
    app.run()

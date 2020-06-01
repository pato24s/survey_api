from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey

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
    password = db.Column(db.String(32))
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


@app.route('/db_test')
def hello_world2():
    new_user = User(name='username', email='patosticco@gmail.com', password='123')
    db.session.add(new_user)
    db.session.commit()
    return 'ok'


if __name__ == '__main__':
    app.run()

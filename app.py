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
    questions = relationship("Question", backref='creator')
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
    questions = relationship("Question", backref='survey')
    creator_id = Column(Integer, ForeignKey('users.id'))


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    answers = relationship("Answer", backref='question')
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


@app.route('/api/users/<user_id>/questions', methods=['GET'])
def get_questions_from_user(user_id):
    user = User.query.get(user_id)
    questions = user.questions
    response = {}
    for question in questions:
        response[question.id] = question.text
    return jsonify(response)


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
    persist_entity(user)
    response = jsonify("User correctly created.")
    return response


@app.route('/api/surveys', methods=['GET'])
def get_all_surveys():
    surveys = Survey.query.all()
    response = []
    for survey in surveys:
        questions_data = []
        for question in survey.questions:
            answers_data = []
            for answer in question.answers:
                answer_data = {
                    answer.id: answer.text
                }
                answers_data.append(answer_data)
            question_data = {
                'title': question.text,
                'answers': answers_data
            }
            questions_data.append(question_data)
        survey_data = {
            'survey_id': survey.id,
            'tags': survey.tags,
            'questions': questions_data
        }
        response.append(survey_data)
    return jsonify(response)


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
    persist_entity(survey)
    response = jsonify("Survey correctly created.")
    return response


@app.route('/api/surveys/<survey_id>/questions', methods=['POST'])
@auth.login_required
def add_question(survey_id):
    question_title = request.form.get('question_title')
    answer_1 = request.form.get('answer_1')
    answer_2 = request.form.get('answer_2')
    answer_3 = request.form.get('answer_3')
    answer_4 = request.form.get('answer_4')
    if answer_1 is None and answer_2 is None and answer_3 is None and answer_4 is None:
        response = jsonify("Cant add question without answers.")
        response.status_code = 400
        return response
    if len(request.form) > 5:
        response = jsonify("Cant create question with more than four answers.")
        response.status_code = 400
        return response
    email = request.authorization.username
    creator = User.query.filter_by(email=email).first()
    survey = Survey.query.get(survey_id)
    question = Question(text=question_title, survey=survey, creator=creator)
    persist_entity(question)
    if answer_1 is not None:
        create_answer_for(answer_1, question)
    if answer_2 is not None:
        create_answer_for(answer_2, question)
    if answer_3 is not None:
        create_answer_for(answer_3, question)
    if answer_4 is not None:
        create_answer_for(answer_4, question)
    return "Question and answers submitted correctly"




def create_answer_for(answer_1, question):
    answer = Answer(text=answer_1, question=question)
    persist_entity(answer)


def persist_entity(entity):
    db.session.add(entity)
    db.session.commit()

if __name__ == '__main__':
    app.run()

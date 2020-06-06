from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import Table, Column, Integer, ForeignKey
from passlib.apps import custom_app_context as pwd_context
from flask_migrate import Migrate
import ast

from sqlalchemy.orm import relationship

# initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/surveys_api"

# extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()


class SelectedAnswer(db.Model):
    __tablename__ = 'selected_answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answers.id'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(32))
    password = db.Column(db.String(128))
    surveys = relationship("Survey", backref='creator')
    questions = relationship("Question", backref='creator')

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
    selected_answers = relationship("Answer", secondary='selected_answers')


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
                'answers': answers_data,
                'id': question.id
            }
            questions_data.append(question_data)
        survey_data = {
            'survey_id': survey.id,
            'tags': survey.tags,
            'title': survey.title,
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
    return jsonify("Question and answers submitted correctly.")


@app.route('/api/surveys/<survey_id>/submit_response', methods=['POST'])
def submit_answer_for(survey_id):
    answers_data = request.form.get('answers_data')
    answers_data_list = ast.literal_eval(answers_data)
    for answer_data in answers_data_list:
        question_id = answer_data[0]
        answer_id = answer_data[1]
        selected_answer = SelectedAnswer(question_id=question_id, answer_id=answer_id)
        persist_entity(selected_answer)
    return jsonify("Survey completed correctly")


@app.route('/api/surveys/<survey_id>/results', methods=['GET'])
def get_results_for(survey_id):
    survey = Survey.query.get(survey_id)
    questions = survey.questions
    questions_data = {
        'survey title': survey.tags,
        'questions results': []
    }
    for question in questions:
        question_data = {
            'question title': question.text
        }
        question_id = question.id
        answers = question.answers
        answers_data = {}
        total_answers = SelectedAnswer.query.filter_by(question_id=question_id).count()
        if total_answers is 0:
            break
        for answer in answers:
            answer_id = answer.id
            number_of_answers = SelectedAnswer.query.filter_by(question_id=question_id, answer_id=answer_id).count()
            answers_data[answer.text] = round((number_of_answers / total_answers) * 100, 2)
        question_data['results'] = answers_data
        questions_data['questions results'].append(question_data)
    return jsonify(questions_data)


def create_answer_for(answer_1, question):
    answer = Answer(text=answer_1, question=question)
    persist_entity(answer)


def persist_entity(entity):
    db.session.add(entity)
    db.session.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0')

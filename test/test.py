from unittest.mock import patch

from flask import Flask

import app
import unittest
from app import db, User

HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404


class apiTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        app.app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/surveys_api_test"
        self.app = app.app.test_client()
        db.create_all()
        return app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_incomplete_register_user_data(self):
        payload = {'username': 'username',
                   'email': 'test@mail.com'}
        response = self.app.post('/api/users', data=payload)

        self.assertEqual(response.json, "Missing arguments.")
        self.assertEqual(response.status_code, 400)

    def test_complete_register_data_creates_user(self):
        payload = {'username': 'username',
                   'email': 'test@mail.com',
                   'password': '123'}
        response = self.app.post('/api/users', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.query.filter_by(email='test@mail.com').first())

    def test_cannot_create_more_than_one_user_with_same_email(self):
        payload = {'username': 'username',
                   'email': 'test@mail.com',
                   'password': '123'}
        response = self.app.post('/api/users', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.query.filter_by(email='test@mail.com').first())

        response = self.app.post('/api/users', data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, "Email is invalid or already taken.")


if __name__ == '__main__':
    unittest.main()

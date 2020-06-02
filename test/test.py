from unittest.mock import patch

import app
import unittest

HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404


class apiTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_incomplete_register_user_data(self):
        payload = {'username': 'username',
                   'email': 'test@mail.com'}
        response = self.app.post('/api/users', data=payload)

        self.assertEqual(response.json, "Missing arguments.")
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()

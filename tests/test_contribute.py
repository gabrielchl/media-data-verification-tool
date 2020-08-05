import json
import unittest

# from mdvt.my.util import get_contributions
from tests.test import MdvtTest


class ContributeTest(MdvtTest):
    # Route

    def test_contribute(self):
        response = self.app.get('/my/contributions', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # also check if it redirects to login page

    def test_contribute_logged_in(self):
        with self.app:
            # session['user_id'] = self.test_user.id
            # session['username'] = self.test_user.username
            response = self.app.get('/my/contributions', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_api_get_media(self):
        with self.app.session_transaction() as session:
            session['user_id'] = 1
        response = self.app.get('/api/get-media', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['status'],
            'success')

    def test_api_contribute_get_request(self):
        response = self.app.get('/api/contribute', follow_redirects=True)
        self.assertEqual(response.status_code, 405)

    def test_api_contribute_not_logged_in(self):
        response = self.app.post('/api/contribute', follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['data']['title'],
            'User is not logged in')

    def test_api_contribute_empty_request(self):
        with self.app.session_transaction() as session:
            session['user_id'] = self.test_user_id
            session['username'] = self.test_username
        response = self.app.post('/api/contribute', follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['data']['title'],
            'Empty request data')

    def test_api_contribute_no_csrf(self):
        with self.app.session_transaction() as session:
            session['user_id'] = self.test_user_id
            session['username'] = self.test_username
        response = self.app.post('/api/contribute', json={},
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['data']['title'],
            'Missing CSRF token')

    def test_api_contribute_wrong_csrf(self):
        with self.app.session_transaction() as session:
            session['user_id'] = self.test_user_id
            session['username'] = self.test_username
        response = self.app.post('/api/contribute', json={
            'csrf': 't409t823irji23'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['data']['title'],
            'CSRF token not recognized')

    def test_api_contribute(self):
        with self.app.session_transaction() as session:
            session['user_id'] = self.test_user_id
            session['username'] = self.test_username
        response = self.app.get('/api/get-media', follow_redirects=True)

        response_data = json.loads(response.get_data(as_text=True))['data']

        question_id = response_data['question_id']
        csrf = response_data['csrf']

        response = self.app.post('/api/contribute', json={
            'question_id': question_id,
            'status': False,
            'csrf': csrf
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_data(as_text=True))['status'],
            'success')

    def test_api_public_query_contrib(self):
        response = self.app.get('/api/query/contributions',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_api_public_query_user(self):
        response = self.app.get('/api/query/users',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Util


if __name__ == '__main__':
    unittest.main()

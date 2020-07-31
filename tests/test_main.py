import unittest

from tests.test import MdvtTest


class MainTest(MdvtTest):
    def test_not_found_error(self):
        response = self.app.get('/a-link-30yu40ro41t9', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_home(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_favicon(self):
        response = self.app.get('/favicon.ico', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # TODO: somehow test the login process

    def test_login(self):
        self.app.get('/login')
        with self.app.session_transaction() as session:
            self.assertEqual(session.get('return_url'), None)

    def test_login_with_return_url(self):
        self.app.get('/login/test-url')
        with self.app.session_transaction() as session:
            self.assertEqual(session.get('return_url'), 'test-url')

    # TODO: should probably test using random return url

    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        with self.app.session_transaction() as session:
            self.assertEqual(len(session.keys()), 0)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

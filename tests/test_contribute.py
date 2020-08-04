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

    # Util


if __name__ == '__main__':
    unittest.main()

import unittest

from tests.test import MdvtTest


class MainTest(MdvtTest):
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

import unittest

from mdvt import app, db
from mdvt.config.config import config


class MdvtTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = config['TEST_DATABASE_URI']
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.drop_all()


if __name__ == '__main__':
    unittest.main()

import unittest

from mdvt import app, db
from mdvt.config.config import config
from mdvt.database.models import User


class MdvtTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = config['TEST_DATABASE_URI']
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        user = User(
            sul_id=12345,
            username='test_user'
        )
        db.session.add(user)
        db.session.commit()

        self.test_user_id = user.id
        self.test_username = user.username

    def tearDown(self):
        db.drop_all()


if __name__ == '__main__':
    unittest.main()

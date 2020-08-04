import unittest

from mdvt import db
from mdvt.database.models import Contribution, Question
# from mdvt.my.util import get_contributions
from tests.test import MdvtTest


class MyTest(MdvtTest):
    # Route

    def test_contributions(self):
        response = self.app.get('/my/contributions', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Util

    def test_get_contributions(self):
        with self.app.session_transaction() as session:
            session['user_id'] = 1

        question = Question(
            page_id=12345,
            type='P180',
            claim_id='test_claim_id',
            depict_value='test_depict_value'
        )
        db.session.add(question)
        db.session.commit()

        contribution = Contribution(
            user_id=self.test_user_id,
            question_id=question.id,
            answer='true'
        )
        db.session.add(contribution)
        db.session.commit()

        # TODO: Fix "RuntimeError: Working outside of request context."

        # print(get_contributions())
        # self.assertEqual(get_contributions(), 696969)


if __name__ == '__main__':
    unittest.main()

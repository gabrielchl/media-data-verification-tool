from flask import session

from mdvt import db
from mdvt.database.models import Contribution, Question


def get_contributions():
    return (db.session.query(Contribution, Question)
            .filter(Contribution.user_id == session.get('user_id'))
            .join(Question, Contribution.question_id == Question.id)
            .all())

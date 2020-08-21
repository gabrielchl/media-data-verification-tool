from flask import session
from sqlalchemy.sql.expression import null, literal

from mdvt import db
from mdvt.database.models import (Contribution, Question,
                                  TestContribution, TestQuestion)


def get_contributions():
    contribs = (db.session.query(Contribution, Question)
                .with_entities(Contribution.id,
                               Contribution.user_id,
                               Contribution.question_id,
                               Contribution.answer,
                               Contribution.undo,
                               Contribution.time_created,
                               Question.id,
                               Question.page_id,
                               Question.type,
                               Question.claim_id,
                               Question.depict_value,
                               Question.qualifier_value,
                               null(),
                               literal('contrib').label('contrib_type'))
                .filter(Contribution.user_id == session.get('user_id'))
                .join(Question, Contribution.question_id == Question.id))
    test_contribs = (db.session.query(TestContribution, TestQuestion)
                     .with_entities(TestContribution.id,
                                    TestContribution.user_id,
                                    TestContribution.question_id,
                                    TestContribution.answer,
                                    null(),
                                    TestContribution.time_created,
                                    TestQuestion.id,
                                    TestQuestion.page_id,
                                    TestQuestion.type,
                                    null(),
                                    TestQuestion.value,
                                    null(),
                                    TestQuestion.correct_ans,
                                    literal('test').label('contrib_type'))
                     .filter(TestContribution.user_id
                             == session.get('user_id'))
                     .join(TestQuestion,
                           TestContribution.question_id == TestQuestion.id))
    return (contribs.union(test_contribs)
                    .order_by(Contribution.time_created.desc())
                    .all())

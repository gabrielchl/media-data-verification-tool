from flask import Blueprint, render_template, session

from mdvt.contribute.util import (get_contrib_count,
                                  get_test_contrib_count,
                                  get_test_contrib_score)
from mdvt.my.util import get_contributions

my_bp = Blueprint('my', __name__)


@my_bp.route('/my/contributions')
def contributions():
    return render_template(
        'my/contributions.html',
        title='My Contributions',
        username=session.get('username', None),
        stat_contributions=get_contrib_count(session.get('user_id', None)),
        stat_tests=get_test_contrib_count(session.get('user_id', None)),
        stat_all_score=get_test_contrib_score(session.get('user_id', None)),
        stat_10_score=get_test_contrib_score(session.get('user_id', None), 10),
        contributions=get_contributions())

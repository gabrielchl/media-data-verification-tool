from flask import Blueprint, render_template, session

from mdvt.my.util import get_contributions

my_bp = Blueprint('my', __name__)


@my_bp.route('/my/contributions')
def contributions():
    return render_template('my/contributions.html',
                           title='My Contributions',
                           username=session.get('username', None),
                           contributions=get_contributions())

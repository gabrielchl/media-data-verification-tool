from flask import (Blueprint, jsonify, render_template, redirect, request,
                   session, url_for)

from mdvt.contribute.util import get_questions
from mdvt import db
from mdvt.database.models import Contribution
from mdvt.database.util import db_set_or_update_user_setting
from mdvt.main.util import is_logged_in

contribute_bp = Blueprint('contribute', __name__)


@contribute_bp.route('/contribute')
def contribute():
    if not is_logged_in():
        return redirect(url_for('main.login'))

    filter_type = request.args.get('filter-type', 'recent')
    db_set_or_update_user_setting(session.get('user_id'),
                                  'filter_type',
                                  filter_type)

    filter_category = request.args.get('category')
    if filter_category:
        db_set_or_update_user_setting(session.get('user_id'),
                                      'filter_category',
                                      filter_category)

    filter_tag = request.args.get('tag').replace('_', ' ')
    if filter_tag:
        db_set_or_update_user_setting(session.get('user_id'),
                                      'filter_tag',
                                      filter_tag)

    return render_template('contribute/contribute.html',
                           title='Contribute',
                           username=session.get('username', None))


@contribute_bp.route('/api/get-media')
def api_get_media():
    filter_type = request.args.get('filter_type', 'recent')
    if filter_type == 'recent':
        filter_value = None
    elif filter_type == 'category':
        filter_value = request.args.get('filter_value')
    else:
        filter_value = request.args.get('filter_value').replace('_', ' ')

    return jsonify({
        'status': 'success',
        'data': get_questions(filter_type, filter_value)
    })


@contribute_bp.route('/api/contribute', methods=['post'])
def api_contribute():
    """Handles contribution requests.

    Expected request format, in json:
    {
        question_id: <question id>,
        status: <true / false / skip>
        csrf: <csrf value>
    }
    """
    if not is_logged_in():
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'User is not logged in'
            }
        }), 401

    if 'csrf' not in request.get_json():
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'Missing CSRF token'
            }
        }), 401

    if request.get_json()['csrf'] != session['csrf'][1]:
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'CSRF token not recognized'
            }
        }), 401

    if request.get_json()['question_id'] != session['csrf'][0]:
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'Wrong question ID'
            }
        }), 401

    contrib_request = request.get_json()
    print(contrib_request)

    db.session.add(Contribution(user_id=session['user_id'],
                                question_id=contrib_request['question_id'],
                                answer=contrib_request['status']))
    db.session.commit()

    session['csrf'] = None
    return jsonify({
        'status': 'success',
        'data': {
            'name': 'success'
        }
    })

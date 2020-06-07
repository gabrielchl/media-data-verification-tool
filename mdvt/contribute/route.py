from flask import (Blueprint, jsonify, render_template, redirect, request,
                   session, url_for)

from mdvt.contribute.util import get_contrib_request
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
        'data': get_contrib_request(filter_type, filter_value)
    })


@contribute_bp.route('/api/contribute', methods=['post'])
def api_contribute():
    """Handles contribution requests.

    Expected request format, in json:
    {
        type: <type of the contribution (e.g. P180)>,
        data: <data, format specificed below>
        csrf: <csrf value>
    }

    Data format for depicts:
    {
        claim_id: <claim id>,
        status: <true / false / skip>
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

    if request.get_json()['csrf'] != session['csrf']:
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'CSRF token not recognized'
            }
        }), 401

    contrib_request = request.get_json()
    print(contrib_request)

    db.session.add(Contribution(user_id=session['user_id'],
                                page_id=0,
                                question='{{type: {}, claim_id: {}}}'.format(
                                    contrib_request['type'],
                                    contrib_request['data']['claim_id']),
                                answer=contrib_request['data']['status']))
    db.session.commit()

    session['csrf'] = None
    return jsonify({
        'status': 'success',
        'data': {
            'name': 'success'
        }
    })

from flask import (Blueprint, jsonify, render_template, redirect, request,
                   session, url_for)

from mdvt.contribute.util import (get_contrib_count, get_questions,
                                  get_test_contrib_count,
                                  get_test_contrib_score, get_test_questions)
from mdvt import db
from mdvt.database.models import (Contribution, Question,
                                  TestContribution, TestQuestion, User)
from mdvt.database.util import db_set_or_update_user_setting
from mdvt.main.util import is_logged_in

from datetime import datetime

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

    filter_tag = request.args.get('tag')
    if filter_tag:
        filter_tag = filter_tag.replace('_', ' ')
    if filter_tag:
        db_set_or_update_user_setting(session.get('user_id'),
                                      'filter_tag',
                                      filter_tag)

    return render_template('contribute/contribute.html',
                           title='Contribute',
                           username=session.get('username', None))


@contribute_bp.route('/api/get-media')
def api_get_media():
    if (not get_contrib_count(session['user_id'])
            and (get_test_contrib_score(session['user_id']) < 0.8
                 or get_test_contrib_count(session['user_id']) < 5)
            and TestQuestion.query.count()):
        return jsonify({
            'status': 'success',
            'data': get_test_questions()
        })
    else:
        question_type = request.args.get('question_type', None)
        filter_type = request.args.get('filter_type', 'recent')
        if filter_type == 'recent':
            filter_value = None
        elif filter_type == 'category':
            filter_value = request.args.get('filter_value')
        else:
            filter_value = request.args.get('filter_value').replace('_', ' ')
        return jsonify({
            'status': 'success',
            'data': get_questions(question_type, filter_type, filter_value)
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

    if not request.data:
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'Empty request data'
            }
        }), 401

    if 'csrf' not in request.get_json():
        return jsonify({
            'status': 'fail',
            'data': {
                'title': 'Missing CSRF token'
            }
        }), 401

    if ('csrf' not in session
            or request.get_json()['csrf'] != session['csrf'][1]):
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
    session['csrf'] = None

    contrib_request = request.get_json()

    if (isinstance(contrib_request['question_id'], str)
            and contrib_request['question_id'][:1] == 'T'):
        question_id = int(contrib_request['question_id'][1:])
        db.session.add(TestContribution(user_id=session['user_id'],
                                        question_id=question_id,
                                        answer=contrib_request['status']))
        db.session.commit()
        correct_ans = (TestQuestion.query
                       .filter(TestQuestion.id == question_id)
                       .first()
                       .correct_ans)
        correct = ('correct'
                   if correct_ans == contrib_request['status']
                   else 'wrong')

        return jsonify({
            'status': 'success',
            'data': {
                'name': 'Test result: {}'.format(correct)
            }
        })
    else:
        db.session.add(Contribution(user_id=session['user_id'],
                                    question_id=contrib_request['question_id'],
                                    answer=contrib_request['status']))
        db.session.commit()
        return jsonify({
            'status': 'success',
            'data': {
                'name': 'Contribution recorded.'
            }
        })


@contribute_bp.route('/api/query/contributions')
def api_public_query_contrib():
    contribs = db.session.query(Contribution, Question).join(Question)

    question_filters = ['page_id', 'type', 'claim_id',
                        'depict_value', 'qualifier_value']
    for question_filter in question_filters:
        filter_value = request.args.get(question_filter)
        if filter_value:
            contribs = contribs.filter(
                       getattr(Question, question_filter) == filter_value)

    contrib_filters = ['user_id']
    for contrib_filter in contrib_filters:
        filter_value = request.args.get(contrib_filter)
        if filter_value:
            contribs = contribs.filter(
                       getattr(Contribution, contrib_filter) == filter_value)

    contribs = contribs.all()
    ret = []
    for contrib in contribs:
        ret.append({
            'id': contrib[0].id,
            'user_id': contrib[0].user_id,
            'time_created': datetime.timestamp(contrib[0].time_created),
            'page_id': contrib[1].page_id,
            'type': contrib[1].type,
            'depict_value': contrib[1].depict_value,
            'qualifier_value': contrib[1].qualifier_value,
            'answer': contrib[0].answer == 'true'
        })
    return jsonify(ret)


# TODO: get contrib score in 1 query
@contribute_bp.route('/api/query/users')
def api_public_query_user():
    users = User.query

    filters = ['sul_id']
    for filter in filters:
        filter_value = request.args.get(filter)
        if filter_value:
            users = users.filter(
                       getattr(User, filter) == filter_value)

    users = users.all()
    ret = []
    for user in users:
        ret.append({
            'id': user.id,
            'sul_id': user.sul_id,
            'all_time_score': get_test_contrib_score(user.id)
        })
    return jsonify(ret)

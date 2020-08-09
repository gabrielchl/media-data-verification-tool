from flask import (Blueprint, jsonify, render_template, redirect, request,
                   session, url_for)
from flask_babel import gettext

from mdvt.contribute.util import (get_contrib_count, get_questions,
                                  get_test_contrib_count,
                                  get_test_contrib_score, get_test_questions,
                                  make_edit_call)
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


@contribute_bp.route('/api/get-question-text')
def api_get_question_text():
    '''
    Gets the question text with place holders ('[DEPICT]', '[MEDIA]'
    and '[QUALIFIER]')

    Parameters
    ----------
    None

    Returns
    -------
    A json object with the list of question text in object.data in the format:
    '{question_type}': '{question text}'
    For example:
    'P180': 'Is [DEPICT] in the above [MEDIA]?'
    '''

    questions = {
        'P180': gettext('Is [DEPICT] in the above [MEDIA]?'),
        'rank': gettext('Is [DEPICT] porminent in the above [MEDIA]?'),
        'P2677': gettext('Is [DEPICT] in the frame in the above [MEDIA]?'),
        'P1354': gettext('Is [DEPICT] in the above [MEDIA] shown with '
                         '[QUALIFIER] (on it)?'),
        'P462': gettext('Is [DEPICT] in the above [MEDIA] have the color '
                        '[QUALIFIER]?'),
        'P518': gettext('Is [DEPICT] at the [QUALIFIER] part of the above '
                        '[MEDIA]?'),
        'P1114': gettext('Are there [QUALIFIER] [DEPICT](s) in the above '
                         '[MEDIA]?'),
        'P4878': gettext('Does the [DEPICT] in the above [MEDIA] symbolize '
                         '[QUALIFIER]?'),
        'P3828': gettext('Is [DEPICT] in the above [MEDIA] wearing (a) '
                         '[QUALIFIER]?'),
        'P710': gettext('Is [QUALIFIER] a participant in [DEPICT] in the '
                        'above [MEDIA]?'),
        'P1419': gettext('Is the [DEPICT] in the above [MEDIA] in [QUALIFIER] '
                         'shape?'),
        'P6022': gettext('Is [DEPICT] in the above [MEDIA] having the '
                         'expression, gesture or body pose [QUALIFIER]?'),
        'P186': gettext('Is [QUALIFIER] used in the [DEPICT] in the above '
                        '[MEDIA]?'),
        'P1884': gettext('Does [DEPICT] in the above [MEDIA] have '
                         '[QUALIFIER]?'),
        'P1552': gettext('Is [QUALIFIER] a quality of [DEPICT] in the above '
                         '[MEDIA]?'),
        'P1545': gettext('Does the [DEPICT] in the above [MEDIA] have the '
                         'series ordinal [QUALIFIER]?'),
        'P7380': gettext('Is the [DEPICT] in the above [MEDIA] identified by '
                         '[QUALIFIER]?'),
        'P149': gettext('Is the [DEPICT] in the above [MEDIA] of [QUALIFIER] '
                        '(style)?')
    }

    return jsonify({
        'status': 'success',
        'data': questions
    })


@contribute_bp.route('/api/get-media')
def api_get_media():
    '''
    Gets a question.
    Note: if the user's score is under a set threadshold, a test question will
    be shown instead

    Parameters
    ----------
    None

    Returns
    -------
    A json object with the question in object.data with the following keys:
    question_id, type, media_page, media_page_id, media_title, depict_id,
    rank, qualifier, depict_label, depict_description, claim_id, csrf
    '''

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
    '''
    Handles contribution requests. Expcts post data in the following format:
    {
        question_id: <question id>,
        status: <true / false / skip>
        csrf: <csrf value>
    }

    Parameters
    ----------
    None

    Returns
    -------
    A json object with the status in object.status of the value 'success' or
    'fail'
    '''

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

    if ('csrf' not in session or not session['csrf']
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
        question = (Question.query
                    .filter(Question.id == contrib_request['question_id'])
                    .first())
        if question.type == 'rank':
            current_rank = question.qualifier_value
            if ((current_rank == 'normal'
                 and contrib_request['status'] == 'true')
                or (current_rank == 'preferred'
                    and contrib_request['status'] == 'false')):

                if contrib_request['status'] == 'true':
                    correct_rank = 'preferred'
                else:
                    correct_rank = 'normal'
                params = {
                    'action': 'wbsetclaim',
                    'format': 'json',
                    'claim': {
                        "type": "statement",
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P180",
                            "datavalue": {
                                "type": "wikibase-entityid",
                                "value": {
                                    "id": question.depict_value
                                }
                            }
                        },
                        "id": question.claim_id,
                        "rank": correct_rank
                    }
                }
                make_edit_call(params)
        if question.type == 'P180':
            if contrib_request['status'] == 'false':
                params = {
                    'action': 'wbremoveclaims',
                    'format': 'json',
                    'claim': question.claim_id
                }
                make_edit_call(params)

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


@contribute_bp.route('/api/contributions')
def api_public_query_contrib():
    '''
    Gets a list of contributions.

    Parameters
    ----------
    None

    Returns
    -------
    A list of objects in json with the following keys for each contribution:
    id, user_id, time_created, page_id, type, depict_value, qualifier_value,
    answer
    '''
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
@contribute_bp.route('/api/users')
def api_public_query_user():
    '''
    Gets a list of users.

    Parameters
    ----------
    None

    Returns
    -------
    A list of objects in json with the following keys for each contribution:
    id, sul_id, all_time_score
    '''
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

from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)
import mwoauth

from mdvt import app
from mdvt.config.config import config
from mdvt.database.models import User
from mdvt.database.util import db_insert_if_not_exist, db_get_user_setting

main_bp = Blueprint('main', __name__)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/404.html'), 404


@main_bp.route('/')
def home():
    if 'username' in session:
        default_filter_type = db_get_user_setting(session['user_id'],
                                                  'filter_type')
        default_filter_category = db_get_user_setting(session['user_id'],
                                                      'filter_category')
        default_filter_tag = db_get_user_setting(session['user_id'],
                                                 'filter_tag')

    if ('username' not in session
        or all(value is None for value in [default_filter_type,
                                           default_filter_category,
                                           default_filter_tag])):
        default_filter_type = 'tag'
        default_filter_category = ''
        default_filter_tag = 'OAuth CID: 1393'

    tags = [
        ['OAuth CID: 1393',
         'OAuth_CID:_1393',
         'ISA Tool'],
        ['computer-aided-tagging',
         'computer-aided-tagging',
         'Computer-aided Tagging']
    ]

    default_filter_tag_name = ''
    for tag in tags:
        if default_filter_tag == tag[0]:
            default_filter_tag_name = tag[2]
            break

    return render_template('main/home.html',
                           title='Home',
                           username=session.get('username', None),
                           default_filter_type=default_filter_type,
                           default_filter_category=default_filter_category,
                           default_filter_tag=default_filter_tag,
                           default_filter_tag_name=default_filter_tag_name,
                           tags=tags)


@main_bp.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@main_bp.route('/login', defaults={'return_url': None})
@main_bp.route('/login/<path:return_url>')
def login(return_url):
    if return_url:
        session['return_url'] = return_url
    consumer_token = mwoauth.ConsumerToken(
        config['OAUTH_TOKEN'], config['OAUTH_SECRET'])
    redirect_url, request_token = mwoauth.initiate(
        config['OAUTH_URI'], consumer_token)
    session['request_token'] = dict(zip(request_token._fields, request_token))
    return redirect(redirect_url)


@main_bp.route('/oauth-callback')
def oauth_callback():
    consumer_token = mwoauth.ConsumerToken(config['OAUTH_TOKEN'],
                                           config['OAUTH_SECRET'])
    access_token = mwoauth.complete(
        config['OAUTH_URI'], consumer_token,
        mwoauth.RequestToken(**session['request_token']), request.query_string)
    identity = mwoauth.identify(
        config['OAUTH_URI'], consumer_token, access_token)

    user = db_insert_if_not_exist(
        User(sul_id=identity['sub'], username=identity['username']),
        sul_id=identity['sub'])

    session['user_id'] = user.id
    session['username'] = user.username
    session['access_token'] = dict(zip(access_token._fields, access_token))
    return redirect(session.pop('return_url', url_for('main.home')))


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

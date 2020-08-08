from flask import Flask, session
from flask_babel import Babel
from flask_babel_js import BabelJS
from flask_sqlalchemy import SQLAlchemy

from mdvt.config.config import config

import os

app = Flask(__name__)

app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI']
app.config['JSON_SORT_KEYS'] = False
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.getcwd() + '/translations'

db = SQLAlchemy(app)

babel = Babel(app)
babel_js = BabelJS(app)
from mdvt.database.util import db_get_user_setting


@babel.localeselector
def get_locale():
    locale = db_get_user_setting(session.get('user_id'), 'locale')
    if locale:
        return locale
    else:
        return 'en_UK'


@babel.timezoneselector
def get_timezone():
    timezone = db_get_user_setting(session.get('user_id'), 'timezone')
    if timezone:
        return timezone
    else:
        return 'Etc/UTC'


from mdvt.contribute.route import contribute_bp
from mdvt.main.route import main_bp
from mdvt.my.route import my_bp

app.register_blueprint(main_bp)
app.register_blueprint(contribute_bp)
app.register_blueprint(my_bp)

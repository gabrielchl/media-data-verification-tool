from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from mdvt.config.config import config

app = Flask(__name__)

app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI']
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

from mdvt.contribute.route import contribute_bp
from mdvt.main.route import main_bp
from mdvt.my.route import my_bp

app.register_blueprint(main_bp)
app.register_blueprint(contribute_bp)
app.register_blueprint(my_bp)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/404.html'), 404

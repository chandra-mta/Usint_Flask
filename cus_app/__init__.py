"""
**cus_app/__init__.py**: Initialize the CUS Flask Application

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import _CONFIG_DICT
from itertools import zip_longest
from cus_app.supple.helper_functions import rank_ordr, IterateRecords

bootstrap = Bootstrap()
db = SQLAlchemy()
sess = Session()
login = LoginManager()

function_dict = {
    'zip_longest': zip_longest,
    'set': set,
    'rank_ordr': rank_ordr,
    'enumerate': enumerate
}
def create_app(_configuration_name):
    app = Flask(__name__)
    app.jinja_env.globals.update(function_dict)
    app.config.from_object(_CONFIG_DICT[_configuration_name])
    app.config['SESSION_SQLALCHEMY'] = db #: Must set the SQLAlchemy database for server-side session data after construction
    bootstrap.init_app(app)
    db.init_app(app)
    sess.init_app(app)
    login.init_app(app)
    #
    # --- connect all apps with blueprint
    #
    # --- error handling
    #
    from cus_app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)
    #
    # --- ocat data page
    #
    from cus_app.ocatdatapage import bp as odp_bp

    app.register_blueprint(odp_bp, url_prefix="/ocatdatapage")

    #
    # --- Main Usint Page
    #
    @app.route("/")
    def index():
        return render_template("index.html")
    return app

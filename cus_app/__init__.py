"""
**cus_app/__init__.py**: Initialize the CUS Flask Application

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""
import sys
import signal
import traceback
from itertools import zip_longest

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import _CONFIG_DICT
from cus_app.supple.helper_functions import rank_ordr, approx_equals

#
# --- Flask Additions
#
bootstrap = Bootstrap()
db = SQLAlchemy()
sess = Session()
login = LoginManager()

function_dict = {
    'zip_longest': zip_longest,
    'set': set,
    'rank_ordr': rank_ordr,
    'enumerate': enumerate,
    'approx_equals': approx_equals,
    'zip': zip
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
    #--- Available handler for processing in the event of keyboard interrupts (localhost testing)
    #
    def graceful_shutdown(signal, frame):
        """
        Handler to run operations in app context following keyboard interrupts (localhost testing)
        """
        with app.app_context():
            print("Running graceful shutdown")
            try:
                pass
            except Exception:
                traceback.print_exc()
            finally:
                sys.exit(0)
    #: Register signal for application
    signal.signal(signal.SIGINT, graceful_shutdown)

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
    # --- target parameter status page
    #
    from cus_app.orupdate import bp as oru_bp

    app.register_blueprint(oru_bp, url_prefix="/orupdate")

    #
    # --- Main Usint Page
    #
    @app.route("/")
    def index():
        return render_template("index.html")
    return app

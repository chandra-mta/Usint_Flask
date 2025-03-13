"""
**cus_app/__init__.py**: Initialize the CUS Flask Application

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

from flask import Flask, render_template
from config import _CONFIG_DICT

def create_app(_configuration_name):
    app = Flask(__name__)
    app.config.from_object(_CONFIG_DICT[_configuration_name])
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

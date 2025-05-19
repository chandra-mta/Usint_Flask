"""
TOO Schedule Page
==============

**scheduler/routes.py**: Render the TOO Duty scheduler page.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 19, 2025

"""

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from cus_app.models import register_user
from cus_app.scheduler import bp
import cus_app.supple.database_interface as dbi


@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/',      methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Display the TOO scheduler page.
    """
    schedule_list = dbi.pull_schedule()
    return render_template('scheduler/index.html',
                           schedule_list = schedule_list
                           )
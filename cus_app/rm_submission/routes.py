"""
Remove Submission Page
==============

**rm_submission/routes.py**: Render the remove submission page.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 15, 2025

"""
import os
import json
from datetime import datetime, timedelta

from flask import render_template, request, session, redirect, url_for
from flask_login import current_user

from cus_app.models import register_user
from cus_app.rm_submission import bp
from cus_app.supple.helper_functions import is_open
import cus_app.supple.database_interface as dbi

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'labels.json')) as f:
    _LABELS = json.load(f)
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

with open(os.path.join(stat_dir, 'color.json')) as f:
    _COLORS = json.load(f)

_36_HOURS_AGO = (datetime.now() - timedelta(days=1.5)).timestamp()

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/',      methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Display the Remove Submission Page
    """
    pass

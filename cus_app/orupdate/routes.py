"""
Target Parameter Status Page
==============

**orupdate/routes.py**: Render the target parameter Status Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 06, 2025

"""
import os
import re
import json
from datetime import datetime

from flask import current_app, render_template, request, flash, session, redirect, url_for, abort
from flask_login    import current_user

from cus_app import db
from cus_app.models import register_user
from cus_app.orupdate import bp
from cus_app.orupdate.forms import SignoffRow
import cus_app.supple.read_ocat_data as rod
import cus_app.supple.database_interface as dbi

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'labels.json')) as f:
    _LABELS = json.load(f)
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/',      methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Prototype
    """
    _NAME_BY_ID = dbi.name_by_id()
    revs = dbi.pull_revision(last=10)
    signoff_forms =[]
    signoff_sqls = []
    for rev in revs:
        sql = dbi.pull_signoff(rev)
        signoff_sqls.append(sql)
        signoff_forms.append(SignoffRow(prefix=str(sql.id)))

    return render_template("orupdate/index.html",
                           signoff_forms = signoff_forms,
                           signoff_sqls = signoff_sqls,
                           _NAME_BY_ID = _NAME_BY_ID
                           )
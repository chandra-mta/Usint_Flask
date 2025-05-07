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

_SIGNOFF_COLUMNS = ('general', 'acis', 'acis_si', 'hrc_si', 'usint') #: Prefix names for the columns of Signoff

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/',      methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Display the Target Parameter Status Page
    """
    _NAME_BY_ID = dbi.name_by_id()
    revs = dbi.pull_revision(last=10)
    open_signoff_forms =[]
    open_signoff_sqls = []
    open_revs =[]

    closed_signoff_sqls = []
    closed_revs = []

    for rev in revs:
        sql = dbi.pull_signoff(rev)
        if is_open(sql):
            open_signoff_sqls.append(sql)
            open_signoff_forms.append(SignoffRow(prefix=str(sql.id)))
            open_revs.append(rev)
        else:
            closed_signoff_sqls.append(sql)
            closed_revs.append(rev)

    return render_template("orupdate/index.html",
                           open_signoff_forms = open_signoff_forms,
                           open_signoff_sqls = open_signoff_sqls,
                           open_revs = open_revs,
                           closed_signoff_sqls = closed_signoff_sqls,
                           closed_revs = closed_revs,
                           _NAME_BY_ID = _NAME_BY_ID
                           )

def is_open(signoff_obj):
    """
    Returns boolean if the signoff entry still needs a signature.
    """
    is_open = False
    for attr in _SIGNOFF_COLUMNS:
        if getattr(signoff_obj, f"{attr}_status") == 'Pending':
            is_open = True
            break
    return is_open

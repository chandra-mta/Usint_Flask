"""
Parameter Check Page
==============

**chkupdata/routes.py**: Render the parameter Check Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 13, 2025

"""
import os
import json
from datetime import datetime, timedelta

from flask import render_template, request, session, redirect, url_for, flash
from flask_login import current_user

from cus_app.models import register_user
from cus_app.chkupdata import bp
from cus_app.chkupdata.forms import ObsidRevForm
import cus_app.supple.database_interface as dbi

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/<obsidrev>', methods=['GET'])
@bp.route('/index/<obsidrev>', methods=['GET'])
def index(obsidrev):
    """
    Display the Target Parameter Status Page
    """
    try:
        obsid, rev = [int(x) for x in obsidrev.split('.')]
    except (ValueError, TypeError):
        flash(f"Ill-formatted Obsid.Rev. {obsidrev}")
        return redirect(url_for('chkupdata.provide_obsidrev'))
    
    return f"<p>{obsid} {rev}</p>"

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def provide_obsidrev():
    obsidrev_form = ObsidRevForm(request.form)
    if request.method == "POST" and obsidrev_form.is_submitted():
        return redirect(url_for('chkupdata.index', obsidrev = obsidrev_form.obsidrev.data))
    return render_template('chkupdata/provide_obsidrev.html',
                           obsidrev_form = obsidrev_form
                           )

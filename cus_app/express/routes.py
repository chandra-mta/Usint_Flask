"""
Express Approval Page
==============

**express/routes.py**: Render the Express Approval Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 12, 2025

"""
import os
import json
from datetime import datetime, timedelta

from flask import current_app, render_template, request, flash, session, redirect, url_for, abort
from flask_login    import current_user

from cus_app import db
from cus_app.models import register_user
from cus_app.express import bp
from cus_app.express.forms import ExpressApprovalForm
import cus_app.supple.read_ocat_data as rod
import cus_app.supple.database_interface as dbi
from cus_app.supple.helper_functions import create_obsid_list

@bp.before_app_request
def before_request():
    if not current_user.is_authenticated:
        register_user()

@bp.route('/',      methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Display the Express Approval Page
    """
    express_form = ExpressApprovalForm(request.form)
    if request.method == 'POST' and express_form.is_submitted():
        #: Redirect to confirmation page, processing the approval.
        try:
            obsid_list = create_obsid_list(express_form.multiobsid.data)
        except (ValueError, TypeError):
            flash("Error in parsing form input. Please verify formatting.")
    return render_template('express/index.html',
                            express_form = express_form
                            )
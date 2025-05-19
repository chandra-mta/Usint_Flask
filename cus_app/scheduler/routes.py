"""
TOO Schedule Page
==============

**scheduler/routes.py**: Render the TOO Duty scheduler page.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 19, 2025

"""
from flask import render_template, request, redirect, url_for
from flask_login import current_user

from cus_app.models import Schedule, register_user
from cus_app.scheduler import bp
from cus_app.scheduler.forms import ScheduleRow
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
    #: Process POST request before displaying schedule data
    if request.method == 'POST':
        for k,v in request.form.to_dict().items():
            if 'Unlock' in v:
                schedule_id = k.split('-')[0]
                #: Unlock requested. Following the PRG design pattern, perform redirect then come back.
                return redirect(url_for('scheduler.unlock', schedule_id = schedule_id))


    schedule_list = dbi.pull_schedule()
    schedule_forms = []
    for entry in schedule_list:
        schedule_forms.append(ScheduleRow(prefix=f"{entry.id}"))
    return render_template('scheduler/index.html',
                           schedule_list = schedule_list,
                           schedule_forms = schedule_forms
                           )


@bp.route('/unlock/<schedule_id>', methods=['GET'])
def unlock(schedule_id):
    dbi.unlock_schedule(schedule_id = schedule_id)
    return redirect(url_for('scheduler.index'))
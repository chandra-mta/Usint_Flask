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
        #
        # --- Only one submit button will be present per request, so iterate and find it
        #
        form_dict = request.form.to_dict()
        for k,v in form_dict.items():
            if 'Unlock' in v:
                schedule_id = k.split('-')[0]
                #: Unlock requested. Following the PRG design pattern, perform redirect then come back.
                return redirect(url_for('scheduler.unlock', schedule_id = schedule_id))
            if 'Update' in v:
                schedule_id = k.split('-')[0]
                user_id = form_dict[f'{schedule_id}-user']
                start_string = form_dict[f"{schedule_id}-start_month"] + "/" + form_dict[f"{schedule_id}-start_day"] + "/" + form_dict[f"{schedule_id}-start_year"]
                stop_string = form_dict[f"{schedule_id}-stop_month"] + "/" + form_dict[f"{schedule_id}-stop_day"] + "/" + form_dict[f"{schedule_id}-stop_year"]
                #: Update requested. Following the PRG design pattern, perform redirect then come back.
                return redirect(url_for('scheduler.update', schedule_id = schedule_id, user_id = user_id, start_string = start_string, stop_string = stop_string))
            if 'Split' in v:
                schedule_id = k.split('-')[0]
                return redirect(url_for('scheduler.split', schedule_id = schedule_id))
            if 'Delete' in v:
                schedule_id = k.split('-')[0]
                return redirect(url_for('scheduler.delete', schedule_id = schedule_id))


    schedule_list = dbi.pull_schedule()
    schedule_forms = []
    for entry in schedule_list:
        form = ScheduleRow(formdata=None, **_prep_form(entry)) #:Set form data to None so that undesirable selections are ignored.
        schedule_forms.append(form)
    return render_template('scheduler/index.html',
                           schedule_list = schedule_list,
                           schedule_forms = schedule_forms
                           )


@bp.route('/unlock/<schedule_id>', methods=['GET'])
def unlock(schedule_id):
    dbi.unlock_schedule_entry(schedule_id = schedule_id)
    return redirect(url_for('scheduler.index'))

@bp.route('/update/<schedule_id>/<user_id>/<start_string>/<stop_string>', methods=['GET'])
def update(schedule_id, user_id, start_string, stop_string):
    dbi.update_schedule_entry(schedule_id, user_id, start_string, stop_string)
    return redirect(url_for('scheduler.index'))

@bp.route('/split/<schedule_id>', methods=['GET'])
def split(schedule_id):
    dbi.split_schedule_entry(schedule_id)
    return redirect(url_for('scheduler.index'))

@bp.route('/delete/<schedule_id>', methods=['GET'])
def delete(schedule_id):
    dbi.delete_schedule_entry(schedule_id)
    return redirect(url_for('scheduler.index'))

def _prep_form(entry):
    """
    Prepare form starting data for the particular entry
    """
    kwarg = {'prefix': str(entry.id)}
    data = {'user': entry.user_id,
            'start_month': entry.start.strftime('%B'),
            'start_day': entry.start.strftime('%d'),
            'start_year': entry.start.strftime('%Y'),
            'stop_month': entry.stop.strftime('%B'),
            'stop_day': entry.stop.strftime('%d'),
            'stop_year': entry.stop.strftime('%Y'),
            }
    kwarg['data'] = data
    return kwarg


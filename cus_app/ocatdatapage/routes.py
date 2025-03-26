"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

from multiprocessing import synchronize
import os
import numpy
import copy
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from wtforms.validators import ValidationError

from flask import current_app, render_template, request
from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import OcatParamForm
import cus_app.supple.read_ocat_data as rod
import cus_app.ocatdatapage.format_ocat_data as fod

_OCAT_DATETIME_FORMAT = (
    "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero.
)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Render Ocat Data In A WTForm
    #
    ocat_data = rod.read_ocat_data(obsid)
    warning = create_warning_line(ocat_data)
    #: Formats information into form and provides additional form-specific parameters
    form_dict = fod.format_for_form(ocat_data)
    form = OcatParamForm(request.form, data=form_dict)
    if request.method == "POST" and form.is_submitted(): 
        #
        #--- Processing Dither Submissions
        #
        if form.open_dither.data:
            #: Refresh the page with the dither entries as initialized by **format_for_form()**
            form.dither_param.dither_flag.data = "Y"
        #
        #--- Processing Time Submissions
        #
        elif form.open_time.data:
            #: Refresh the page with time entries as initialized by **format_for_form()**
            form.time_param.window_flag.data = "Y"
            form = add_time_rank(form)
        elif form.time_param.add_time.data:
            form = add_time_rank(form)
        elif form.time_param.remove_time.data:
            form = remove_time_rank(form)
        #
        #--- Processing Roll Submissions
        #
        elif form.open_roll.data:
            #: Refresh the page with roll entries as initialized by **format_for_form()**
            form.roll_param.roll_flag.data = "Y"
            form = add_roll_rank(form)
        elif form.roll_param.add_roll.data:
            form = add_roll_rank(form)
        elif form.roll_param.remove_roll.data:
            form = remove_roll_rank(form)
        #
        #--- processing Acis Window Submissions
        elif form.open_aciswin.data:
            #: Refresh the page with aciswin entires as initialized by **format_for_form()**
            form.aciswin_param.spwindow_flag.data = "Y"
            form = add_window_rank(form)
        elif form.aciswin_param.add_window.data:
            form = add_window_rank(form)
        elif form.aciswin_param.remove_window.data:
            form = remove_window_rank(form)
        #
        #
        #--- General Refresh
        #
        elif form.refresh.data:
            #: Process the changes submitted to the form for how they would update the form and param_dict objects
            form = fod.synchronize_values(form)
    return render_template("ocatdatapage/index.html", form=form, warning=warning)

#
#--- Helper Functions
#
def add_time_rank(form):
    """
    Add an entry to the time constraints ranking.
    """
    val = form.time_param.time_ordr.data #: TODO fix with field coercion into correct returned data type
    if val not in (None, ''):
        form.time_param.time_ordr.data = int(val) + 1
    else:
        form.time_param.time_ordr.data = 1
    form.time_param.window_constraint.append_entry('Y')
    form.time_param.tstart_year.append_entry(None)
    form.time_param.tstop_year.append_entry(None)
    form.time_param.tstart_month.append_entry(None)
    form.time_param.tstop_month.append_entry(None)
    form.time_param.tstart_date.append_entry(None)
    form.time_param.tstop_date.append_entry(None)
    form.time_param.tstart_time.append_entry("00:00")
    form.time_param.tstop_time.append_entry("00:00")
    return form
    
def remove_time_rank(form):
    """
    Remove all "NA" Entries from the field lists, turning flag off if no entries remain.
    """
    rm_idx = []
    for i, field in enumerate(form.time_param.window_constraint.entries):
        if field.data in (None, 'None'):
            rm_idx.append(i)
    rm_idx = sorted(rm_idx,reverse=True) #: Reverse so that pop method won't interfere with indices later in list.
    subtract_last_index = len(rm_idx)
    if subtract_last_index > 0:
        for field in form.time_param:
            if field.type == 'FieldList':
                for i in rm_idx:
                    field.entries.pop(i)
                field.last_index -= subtract_last_index
        val = int(form.time_param.time_ordr.data) - subtract_last_index #: TODO fix with field coercion with correct returned data type
        form.time_param.time_ordr.data = val
        if form.time_param.time_ordr.data == 0:
            form.time_param.window_flag.data = 'N'
    return form

def add_roll_rank(form):
    """
    Add an entry to the roll constraints ranking.
    """
    val = form.roll_param.roll_ordr.data #: TODO fix with field coercion into correct returned data type
    if val not in (None, ''):
        form.roll_param.roll_ordr.data = int(val) + 1
    else:
        form.roll_param.roll_ordr.data = 1
    form.roll_param.roll_constraint.append_entry('Y')
    form.roll_param.roll_180.append_entry(None)
    form.roll_param.roll.append_entry(None)
    form.roll_param.roll_tolerance.append_entry(None)
    return form

def remove_roll_rank(form):
    """
    Remove all "NA" Entries from the field lists, turning flag off if no entries remain.
    """
    rm_idx = []
    for i, field in enumerate(form.roll_param.roll_constraint.entries):
        if field.data in (None, 'None'):
            rm_idx.append(i)
    rm_idx = sorted(rm_idx,reverse=True) #: Reverse so that pop method won't interfere with indices later in list.
    subtract_last_index = len(rm_idx)
    if subtract_last_index > 0:
        for field in form.roll_param:
            if field.type == 'FieldList':
                for i in rm_idx:
                    field.entries.pop(i)
                field.last_index -= subtract_last_index
        val = int(form.roll_param.roll_ordr.data) - subtract_last_index #: TODO fix with field coercion with correct returned data type
        form.roll_param.roll_ordr.data = val
        if form.roll_param.roll_ordr.data == 0:
            form.roll_param.roll_flag.data = 'N'
    return form

def add_window_rank(form):
    """
    Add an entry to the roll constraints ranking.
    """
    val = form.aciswin_param.aciswin_no.data #: TODO fix with field coercion into correct returned data type
    if val not in (None, ''):
        form.aciswin_param.aciswin_no.data = int(val) + 1
    else:
        form.aciswin_param.aciswin_no.data = 1
    form.aciswin_param.chip.append_entry('I0')
    form.aciswin_param.start_row.append_entry(1)
    form.aciswin_param.start_column.append_entry(1)
    form.aciswin_param.height.append_entry(1023)
    form.aciswin_param.width.append_entry(1023)
    form.aciswin_param.lower_threshold.append_entry(0.08)
    form.aciswin_param.pha_range.append_entry(13.0)
    form.aciswin_param.sample.append_entry(0)
    return form

def remove_window_rank(form):
    """
    Remove all "NA" Entries from the field lists, turning flag off if no entries remain.
    """
    rm_idx = []
    for i, field in enumerate(form.aciswin_param.chip.entries):
        if field.data in (None, 'None'):
            rm_idx.append(i)
    rm_idx = sorted(rm_idx,reverse=True) #: Reverse so that pop method won't interfere with indices later in list.
    subtract_last_index = len(rm_idx)
    if subtract_last_index > 0:
        for field in form.aciswin_param:
            if field.type == 'FieldList':
                for i in rm_idx:
                    field.entries.pop(i)
                field.last_index -= subtract_last_index
        val = int(form.aciswin_param.aciswin_no.data) - subtract_last_index #: TODO fix with field coercion with correct returned data type
        form.aciswin_param.aciswin_no.data = val
        if form.aciswin_param.aciswin_no.data == 0:
            form.aciswin_param.spwindow_flag.data = 'N'
    return form

def create_warning_line(ocat_data):
    """
    Check the observation status and create warning

    :param ocat_data: Ocat Data
    :type ocat_data: dict
    :return: Line detailing warning information
    :rtype: str
    """
    line = ""
    #
    # --- observation status; if not unobserved or schedule, a warning is flashed
    #
    if ocat_data.get("status") in ["unobserved", "scheduled", "untriggered"]:
        pass
    elif ocat_data.get("status") in ["observed", "archived", "triggered"]:
        line = f"This observation was already {ocat_data.get('status').upper()}."
        return line
    else:
        line = f"This observation was {ocat_data.get('status').upper()}."
        return line
    #
    # --- check lts/scheduled observation date
    #
    lts_chk = False
    obs_date = ocat_data.get("soe_st_sched_date")
    if obs_date is None:
        obs_date = ocat_data.get("lts_lt_plan")
        lts_chk = True

    if obs_date is not None:
        time_diff = (
            datetime.strptime(obs_date, _OCAT_DATETIME_FORMAT) - datetime.now()
        ).total_seconds()
        inday = int(time_diff/86400)
        if inday < 0:
            inday = 0
    else:
        time_diff = 1e8
        inday = 1e3
    #
    # --- check whether this observation is on OR list
    #
    ifile = os.path.join(current_app.config["OBS_SS"], "scheduled_obs_list")
    with open(ifile) as f:
        mp_list = [line.strip().split() for line in f.readlines()]
    mp_chk = False
    for ent in mp_list:
        if ent[0] == ocat_data.get('obsid'):
            mp_chk = True
            break
    #
    # --- for the case that lts date is passed but not observed yet
    #
    if lts_chk and time_diff < 0:
        line = "The scheduled (LTS) date of this observation was already passed."

    elif not lts_chk and inday == 0:
        line = "This observation is scheduled for today."
    #
    # --- less than 10 days to scheduled date
    #
    elif time_diff < 864000:
        #
        # --- if the observation is on OR list
        #
        if mp_chk:
            if ocat_data.get("status") == "scheduled":
                line = f"{inday} days left to the scheduled date. You must get a permission from MP to modify entries (Scheduled on: {obs_date}.)"
            else:
                line = f"This observation is currently under review in an active OR list. You must get a permission from MP to modify entries (LTS Date: {obs_date}.)"
        #
        # --- if the observation is not on the OR list yet
        #
        else:
            if lts_chk and ocat_data.get("status") == "unobserved":
                line = f"{inday}  (LTS) days left, but the observation is not scheduled yet. You may want to check whether this is still a possible observation date with MP."
            else:
                if ocat_data["status"][-1] in [
                    "unobserved",
                    "scheduled",
                    "untriggered",
                ]:
                    line = f"This observation is scheduled on {obs_date}."
    #
    # --- if the observation is on OR list, but more than 10 days away
    #
    elif mp_chk:
        line = "This observation is currently under review in an active OR list. You must get a permission from MP to modify entries"
        if lts_chk:
            line += f" (LTS Date: {obs_date}.)"
        else:
            line += f" (Scheduled on: {obs_date}.)"
    return line

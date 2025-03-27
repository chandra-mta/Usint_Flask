"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

import os
import re
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
_COMBINE_DATETIME_FORMAT = "%b%d%Y%H:%M"

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
            form = fod.add_time_rank(form)
        elif form.time_param.add_time.data:
            form = fod.add_time_rank(form)
        elif form.time_param.remove_time.data:
            form = fod.remove_time_rank(form)
        #
        #--- Processing Roll Submissions
        #
        elif form.open_roll.data:
            #: Refresh the page with roll entries as initialized by **format_for_form()**
            form.roll_param.roll_flag.data = "Y"
            form = fod.add_roll_rank(form)
        elif form.roll_param.add_roll.data:
            form = fod.add_roll_rank(form)
        elif form.roll_param.remove_roll.data:
            form = fod.remove_roll_rank(form)
        #
        #--- processing Acis Window Submissions
        #
        elif form.open_aciswin.data:
            #: Refresh the page with aciswin entires as initialized by **format_for_form()**
            form.aciswin_param.spwindow_flag.data = "Y"
            form = fod.add_window_rank(form)
        elif form.aciswin_param.add_window.data:
            form = fod.add_window_rank(form)
        elif form.aciswin_param.remove_window.data:
            form = fod.remove_window_rank(form)
        #
        #--- General Refresh
        #
        elif form.refresh.data:
            #: Process the changes submitted to the form for how they would update the form and param_dict objects
            form = fod.synchronize_values(form)
        #
        #--- Submission
        #
        elif form.submit.data:
            render_finalize_page(form, ocat_data)
    return render_template("ocatdatapage/index.html", form=form, warning=warning)

def render_finalize_page(form, ocat_data):

    #: Read selected submit options ( and perform same actions to multi-obsids)
    form = fod.synchronize_values(form)
    if form.submit_choice.data == 'norm':
        form_dict = form.data
        indicator = indicate_changes(form_dict, ocat_data)

        #: Perform change to the other obsids as well
        if form_dict.get('multiobsid') not in (None,''):
            multi_obsid = create_obsid_list(form_dict.get('multiobsid'), int(form_dict['gen_param'].get('obsid')))
        #create_revision()
    elif form.submit_choice.data == 'asis':
        #create_revision()
        pass
    elif form.submit_choice.data == 'remove':
        #create_revision()
        pass
    elif form.submit_choice.data == 'clone':
        #create_revision()
        pass

def indicate_changes(form_dict, ocat_data):
    """
    Generate indicators of changed parameters and their new values.
    """
    #
    #--- Due to slight differences in the available parameters in the ocat and in the form, we process through their shared keys.
    #
    


    #
    #--- Special Cases
    #
    if form_dict['time_param'].get('window_flag') in ('Y', 'P'):
            tstart, tstop = combine_times(form_dict['time_param']) #: Combine the separate times into two lists of datetime objects
#
#--- Helper Functions
#
def combine_times(time_param):
    """
    Combine times from the form into ordered list of comparison datetime objects.
    """
    tstart = []
    tstop = []
    for i in range(int(time_param.get('time_ordr'))):
        start_string = f"{time_param.get('tstart_month')[i]}"
        stop_string = f"{time_param.get('tstop_month')[i]}"
        start_string += f"{time_param.get('tstart_date')[i]}"
        stop_string += f"{time_param.get('tstop_date')[i]}"
        start_string += f"{time_param.get('tstart_year')[i]}"
        stop_string += f"{time_param.get('tstop_year')[i]}"
        start_string += f"{time_param.get('tstart_time')[i]}"
        stop_string += f"{time_param.get('tstop_time')[i]}"
        tstart.append(datetime.strptime(start_string, _COMBINE_DATETIME_FORMAT))
        tstop.append(datetime.strptime(stop_string, _COMBINE_DATETIME_FORMAT))
    return tstart, tstop

def create_obsid_list(list_string, obsid):
    """
    Create a list of obsids from form input for a parameter display page.
    """
    #: Split the input string into elements
    raw_elements = [x for x in re.split(r'\s+|,|:|;', list_string) if x != '']
    
    #: Combine into string replaceable format for dash parsing
    combined = ','.join(raw_elements)
    combined = combined.replace(',-,','-').replace('-,','-').replace(',-','-')
    
    #: Process Ranges
    obsids_list = []
    for element in combined.split(','):
        if element.isdigit():
            obsids_list.append(int(element))
        else:
            start, end = element.split('-')
            obsids_list.extend(list(range(int(start), int(end) + 1)))
    
    #: Remove duplicates, sort, and exclude the main obsid
    obsids_list = sorted(set(obsids_list) - {obsid})
    return obsids_list


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

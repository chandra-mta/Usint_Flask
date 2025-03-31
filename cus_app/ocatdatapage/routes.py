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

from flask import current_app, render_template, request, session, redirect, url_for
from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import ConfirmForm, OcatParamForm
import cus_app.supple.read_ocat_data as rod
import cus_app.ocatdatapage.format_ocat_data as fod

@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Render Ocat Data In A WTForm
    #
    ocat_data = session.get('ocat_data')
    if ocat_data is None:
        ocat_data = rod.read_ocat_data(obsid)
        session['ocat_data'] = ocat_data
    warning = create_warning_line(ocat_data)
    #: Formats information into form and provides additional form-specific parameters
    form_dict = fod.format_for_form(ocat_data)
    form = OcatParamForm(request.form, data=form_dict)
    if request.method == "POST" and form.is_submitted(): 
        form = fod.synchronize_values(form) #: Process the changes submitted to the form for how they would update the form and param_dict objects
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
            pass #: Only POSTed in order to synchronize values.
        #
        #--- Submission
        #
        elif form.submit.data:
            prepare_confirmation_page(form, ocat_data)
            return redirect(url_for('ocatdatapage.confirm'))
    return render_template("ocatdatapage/index.html", form=form, warning=warning)


@bp.route('/confirm', methods=['GET', 'POST'])
def confirm():
    ind_dict = session.get('ind_dict')
    multi_obsid = session.get('multi_obsid',[])
    ocat_data = session.get('ocat_data')
    form_dict = session.get('form_dict')
    or_dict = {} #: TODO create check for whether the obsid is in the or_list so that the parameter changes can provided the user with a warning.
    form = ConfirmForm(request.form)
    if request.method == "POST" and form.is_submitted():
        pass
    return render_template('ocatdatapage/confirm.html',
                           form = form,
                           ind_dict = ind_dict,
                           multi_obsid = multi_obsid,
                           ocat_data = ocat_data,
                           form_dict = form_dict,
                           or_dict = or_dict)

@bp.route('/finalize', methods=['GET', 'POST'])
def finalize():
    #: TODO make sure that the finalized submission will run the functions to submit the SQLAlchemy commit and then clear the session data
    #: Then display the page informing the user that their revision went through.
    #: Needed so that we can complete a revision action and keep the cache clear (particularly of ocat data) for the next obsid revision
    pass

def prepare_confirmation_page(form, ocat_data):

    #: Read selected submit options (and perform same actions to multi-obsids)
    if form.submit_choice.data == 'norm':
        form_dict = fod.format_for_comparison(form)
        ind_dict = indicate_changes(form_dict, ocat_data)
        session['ind_dict'] = ind_dict
        #: Perform change to the other obsids as well
        if form_dict.get('multiobsid') not in fod._NULL_LIST:
            multi_obsid = create_obsid_list(form_dict.get('multiobsid'), int(form_dict['gen_param'].get('obsid')))
            session['multi_obsid'] = multi_obsid
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
    ind_dict = {}
    for category, parameter_list in fod._DISPLAY_CHANGE_BY_CATEGORY.items():
        ind_dict[category] = {}
        for parameter in parameter_list:
            org = ocat_data.get(parameter)
            new = form_dict[category].get(parameter)
            if not equal_values(org,new):
                ind_dict[category][parameter] = [org,new]
    #
    #--- Special Cases
    #
    #: TODO Clean up implementation for how the indicator_dict is storing changed datetime information.
    form_tstart = None
    form_tstop = None
    ocat_tstart = None
    ocat_tstop = None
    if form_dict['time_param'].get('window_flag') in ('Y', 'P'):
            form_tstart, form_tstop = combine_times(form_dict['time_param']) #: Combine the separate times into two lists of datetime objects
            if ocat_data.get('window_flag') in ('Y', 'P'):
                ocat_tstart = [datetime.strptime(x,fod._OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstart')]
                ocat_tstop = [datetime.strptime(x,fod._OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstop')]
    if (str(form_tstart) != str(ocat_tstart)) or (str(form_tstop) != str(ocat_tstop)):
        ocat_tstart = [x.strftime(fod._OCAT_DATETIME_FORMAT) for x in ocat_tstart]
        ocat_tstop = [x.strftime(fod._OCAT_DATETIME_FORMAT) for x in ocat_tstop]
        form_tstart = [x.strftime(fod._OCAT_DATETIME_FORMAT) for x in form_tstart]
        form_tstop = [x.strftime(fod._OCAT_DATETIME_FORMAT) for x in form_tstop]
        ind_dict[category]['tstart'] = [ocat_tstart, form_tstart]
        ind_dict[category]['tstop'] = [ocat_tstop, form_tstop]
    
    return ind_dict
#
#--- Helper Functions
#
def equal_values(org,new):
    """
    Compare values within reason for a revision.
    """
    if isinstance(org,(int,float)) and isinstance(new,(int,float)):
        return round(org,4) == round(new,4)
    elif isinstance(org,str) and isinstance(new,str):
        return org.replace(" ","") == new.replace(" ","")
    elif isinstance(org,list) and isinstance(new,list):
        return str(org) == str(new)
    elif isinstance(org,datetime) and isinstance(new,datetime):
        diff = (new - org).total_seconds()
        return diff > 60
    else:
        return org == new

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
        tstart.append(datetime.strptime(start_string, fod._COMBINE_DATETIME_FORMAT))
        tstop.append(datetime.strptime(stop_string, fod._COMBINE_DATETIME_FORMAT))
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
            datetime.strptime(obs_date, fod._OCAT_DATETIME_FORMAT) - datetime.now()
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

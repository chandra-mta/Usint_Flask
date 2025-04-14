"""
**ocatdatapage/routes.py**: Render the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

import os
import re
import json
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from wtforms.validators import ValidationError

from flask import current_app, render_template, request, session, redirect, url_for

from cus_app.ocatdatapage import bp
from cus_app.ocatdatapage.forms import ConfirmForm, OcatParamForm
import cus_app.supple.read_ocat_data as rod
import cus_app.ocatdatapage.format_ocat_data as fod


stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'labels.json')) as f:
    _LABELS = json.load(f)

@bp.route("/", methods=["GET", "POST"])
@bp.route("/<obsid>", methods=["GET", "POST"])
@bp.route("/index/<obsid>", methods=["GET", "POST"])
def index(obsid=None):
    #
    # --- Fetch all relevant ocat data in it's current state and store in session.
    # --- Note that the 4KB limitation on client-side cookies means we use flask_session to
    # --- integrate server-side cookie directly into the session table of the usint revision SQL database
    #
    ocat_data, warning, orient_maps, ocat_form_dict = fetch_session_data(obsid)
    #
    # --- Render Ocat Data In A WTForm
    #
    form = OcatParamForm(request.form, data = ocat_form_dict)
    if form.validate_on_submit():
    #if request.method == "POST" and form.is_submitted(): 
        #: Form submitted, send form data to session and go to confirmation page
        ocat_form_dict = fod.format_POST(form.data)
        session[f'ocat_form_dict_{obsid}'] = ocat_form_dict
        return redirect(url_for('ocatdatapage.confirm', obsid = obsid))
    return render_template("ocatdatapage/index.html", 
                           form=form, 
                           warning=warning,
                           ocat_data=ocat_data,
                           orient_maps=orient_maps,
                           _LABELS=_LABELS)


@bp.route('/confirm', methods=['GET', 'POST'])
def confirm(obsid):
    #
    # --- Process the selected radio option for the desired change
    #
    form = ConfirmForm(request.form)
    ocat_data, warning, orient_maps, ocat_form_dict = fetch_session_data(obsid)
    change_dict = fod.determine_changes(ocat_form_dict, ocat_data)
    multi_obsid = create_obsid_list(ocat_form_dict.get('multiobsid'), obsid)
    or_dict = {} #: TODO generate
    if request.method == "POST" and form.is_submitted(): #: no validators
        if form.previous_page:
            #: Got back and edit
            return redirect(url_for('ocatdatapage.index', obsid=obsid))
        elif form.finalize:
            #: Got back and edit
            return redirect(url_for('ocatdatapage.finalize', obsid=obsid))
    return render_template('ocatdatapage/confirm.html',
                           form = form,
                           obsid = obsid,
                           multi_obsid = multi_obsid,
                           ocat_form_dict = ocat_form_dict,
                           ocat_data = ocat_data,
                           change_dict = change_dict,
                           or_dict = or_dict,
                           _LABELS = _LABELS,
                           )

@bp.route('/finalize', methods=['GET', 'POST'])
def finalize(obsid):
    #: TODO make sure that the finalized submission will run the functions to submit the SQLAlchemy commit and then clear the session data
    #: Then display the page informing the user that their revision went through.
    #: Needed so that we can complete a revision action and keep the cache clear (particularly of ocat data) for the next obsid revision
    pass

def fetch_session_data(obsid):
    """
    Possible to get confused midway through a rendering of a form object or storing obsid data
    when working with multiple obsids in a session. This will format them to a specific set related to the input obsid
    """
    ocat_data = session.get(f'ocat_data_{obsid}')
    warning = session.get(f'warning_{obsid}')
    orient_maps = session.get(f'orient_maps_{obsid}')
    flag_override = session.get(f"flag_override_{obsid}")
    if ocat_data is None:
        #: First Fetch
        ocat_data = rod.read_ocat_data(obsid)
        #: Generate form specific copies of ocat data. Added to ocat data to later change comparison.
        form_additions = fod.generate_additional(ocat_data)
        ocat_data.update(form_additions)
        session[f'ocat_data_{obsid}'] = ocat_data
        warning = fod.create_warning_line(ocat_data)
        session[f'warning_{obsid}'] = warning
        orient_maps = fod.create_orient_maps(ocat_data)
        session[f'orient_maps_{obsid}'] = orient_maps
        #
        # --- Create minor overrides for the form display of certain flags
        #
        flag_override = {}
        for flag in ('window_flag', 'roll_flag', 'spwindow_flag'):
            if ocat_data.get(flag) == 'P':
                flag_override[flag] = 'Y'
            elif ocat_data.get(flag) is None:
                flag_override[flag] = 'N'
        session[f'flag_override_{obsid}'] = flag_override
    #
    # --- With the session data related to this specific obsid, we then process whether to 
    # --- generate a new form from the default data or from a previously passed form we are editing again.
    #
    ocat_form_dict = session.get(f'ocat_form_dict_{obsid}', (ocat_data | flag_override))

    return ocat_data, warning, orient_maps, ocat_form_dict

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

#
# --- Old functions kept in case of use
#

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
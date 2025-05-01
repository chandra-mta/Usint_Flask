"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
from datetime import datetime
import os
import json
from flask import current_app
from cus_app.supple.read_ocat_data import check_approval
from cus_app.supple.helper_functions import NULL_LIST, coerce_none, coerce, approx_equals, convert_ra_dec_format, reorient_rank
import itertools

stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'parameter_selections.json')) as f:
    _PARAM_SELECTIONS = json.load(f)

_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero

_FLAG_RANK_COLUMN_ORDR = (
    ('window_flag', 'time_ranks', 'time_columns', 'time_ordr'),
    ('roll_flag', 'roll_ranks', 'roll_columns', 'roll_ordr'),
    ('spwindow_flag', 'window_ranks', 'window_columns', 'window_ordr')
)

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
    
    if check_approval(ocat_data.get('obsid')):
        line = "This Observation Is Already On the Approved List"

    return line

def create_orient_maps(ocat_data):
    #
    #--- Viewing Orientation Maps
    #
    link_part = f"https://cxc.harvard.edu/targets/{ocat_data.get('seq_nbr')}/{ocat_data.get('seq_nbr')}.{ocat_data.get('obsid')}."

    rass = "NoImage"
    rosat = "NoImage"
    dss = "NoImage"
    if os.path.isdir(f"/data/targets/{str(ocat_data.get('seq_nbr'))}"):
        gif_check = ''.join([each for each in os.listdir(f"/data/targets/{str(ocat_data.get('seq_nbr'))}") if each.endswith('.gif')])
        if 'soe.rass.gif' in gif_check:
            rass  = f"{link_part}soe.rass.gif"
        elif 'rass.gif' in gif_check:
            rass  = f"{link_part}rass.gif"

        if 'soe.pspc.gif' in gif_check:
            rosat  = f"{link_part}soe.pspc.gif"
        elif 'pspc.gif' in gif_check:
            rosat  = f"{link_part}pspc.gif"

        if 'soe.dss.gif' in gif_check:
            dss   = f"{link_part}soe.dss.gif"
        elif 'dss.gif' in gif_check:
            dss   = f"{link_part}dss.gif"
    
    orient_maps = {
        'rass': rass,
        'rosat': rosat,
        'dss': dss
    }
    return orient_maps

def generate_additional(ocat_data):
    """Convert certain ocat data parameters to new values for form editing

    :param ocat_data: Ocat Data keyed by parameter directly (Represents only what's in the ocat in original form)
    :type ocat_data: dict(str, value)
    """
    additional = {}
    #
    #--- RA, Dec
    #
    ra = ocat_data.get('ra')
    dec = ocat_data.get('dec')
    if ra is not None and dec is not None:
        ra_hms, dec_dms = convert_ra_dec_format(ra, dec, 'hmsdms')
        additional['ra_hms'] = ra_hms
        additional['dec_dms'] = dec_dms
    #
    # --- Dither
    #
    for key in ('y_amp', 'y_freq', 'z_amp', 'z_freq'):
        val = ocat_data.get(key)
        if val is not None:
            additional[f'{key}_asec'] = val * 3600
    return additional

def clean_POST(input_dict):
    """
    Perform coercion which is ignored in Flask-WTF forms and drop undesired values
    """
    output_dict = {}
    
    for k,v in input_dict.items():
        if k not in _PARAM_SELECTIONS['clean_POST']:
            if isinstance(v,dict):
                output_dict[k] = clean_POST(v)
            else:
                output_dict[k] = coerce_none(v)
    return output_dict

def format_POST(ocat_form_dict):
    """
    Minor changes to listed form data after POST request and preparing ocat_form_dict
    """
    ocat_form_dict = clean_POST(ocat_form_dict)
    
    #: Include ocat-formatted copies of coordinate and dither parameters
    ra, dec = convert_ra_dec_format(ocat_form_dict.get('ra_hms'),ocat_form_dict.get('dec_dms') , 'dd')
    ocat_form_dict['ra'] = ra
    ocat_form_dict['dec'] = dec
    for key in ('y_amp', 'y_freq', 'z_amp', 'z_freq'):
        val = ocat_form_dict.get(f'{key}_asec')
        if val is not None:
            ocat_form_dict[key] = val / 3600

    if ocat_form_dict.get('window_flag') == 'Y':
        #: Check if needs to be preference instead
        check_time = set()
        for rank in ocat_form_dict.get('time_ranks'):
            check_time.add(rank.get('window_constraint'))
        if check_time == set('P'):
            ocat_form_dict['window_flag'] = 'P'

    if ocat_form_dict.get('roll_flag') == 'Y':
        #: Check if needs to be preference instead
        check_roll = set()
        for rank in ocat_form_dict.get('roll_ranks'):
            check_roll.add(rank.get('roll_constraint'))
        if check_roll == set('P'):
            ocat_form_dict['window_flag'] = 'P'
    return ocat_form_dict

def construct_entries(ocat_form_dict, ocat_data):
    """
    Iterate over select keys in the ocat_form_dict to identify revised parameters
    This generates the set of information used in filling out the Originals and Requests tables

    :Note: Original state information entries are all recorded for comparison purposes, but only put into the SQL database if non-null.
    Request change entries are only recorded if the parameter has changed from the Original
    """

    org_dict = {}
    req_dict = {}

    #: Regular Changes
    for param in _PARAM_SELECTIONS['basic_params'] + _PARAM_SELECTIONS['usint_created']:
        org = coerce(ocat_data.get(param))
        req = coerce(ocat_form_dict.get(param))
        org_dict[param] = org 
        if not approx_equals(org, req):
            req_dict[param] = req
    #: Dither Set (This is a special case of a div-dependent flag which doesn't process list changes)
    dither_org, dither_req = process_flag_set(ocat_data, ocat_form_dict, _PARAM_SELECTIONS['dither_params_usint'] + _PARAM_SELECTIONS['dither_params_ocat'], 'dither_flag')
    org_dict.update(dither_org)
    req_dict.update(dither_req)

    #: Rank set
    #: Include copy of the times ranks in columns orientation into the comparison dictionaries
    for flag, ranks, columns, ordr in _FLAG_RANK_COLUMN_ORDR:
        org_columns = reorient_rank(ocat_data.get(ranks), 'columns')
        req_columns = reorient_rank(ocat_form_dict.get(ranks), 'columns')
        if org_columns is not None:
            ocat_data.update(org_columns)
        if req_columns is not None:
            ocat_form_dict.update(req_columns)

        org, req = process_flag_set(ocat_data, ocat_form_dict, _PARAM_SELECTIONS[columns] + [ranks], flag)
        org_dict.update(org)
        req_dict.update(req)

    return org_dict, req_dict

def process_flag_set(ocat_data, ocat_form_dict, param_set, flag):

    org_dict = {k:None for k in param_set}
    req_dict = {}

    #: Flag changes
    if ocat_data.get(flag) == 'N' and ocat_form_dict.get(flag) == 'N':
        return org_dict, req_dict #: No information
    
    elif ocat_data.get(flag) == 'N' and ocat_form_dict.get(flag) in ('Y', 'P'):
        #: No original values, but new requested ones
        for param in param_set:
            req_dict[param] = coerce(ocat_form_dict.get(param))

    elif ocat_data.get(flag) in ('Y', 'P') and ocat_form_dict.get(flag) == 'N':
        #: Original values exist, but must be recorded as nullified
        for param in param_set:
            org_dict[param] = coerce(ocat_data.get(param))
            req_dict[param] = None
    else:
        for param in param_set:
            org = coerce(ocat_data.get(param))
            req = coerce(ocat_form_dict.get(param))
            org_dict[param] = org
            if not approx_equals(org, req):
                req_dict[param] = req
    return org_dict, req_dict
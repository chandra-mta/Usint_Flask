"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
from astropy.coordinates import Angle
from datetime import datetime
import os
from flask import current_app
from cus_app.supple.read_ocat_data import check_approval
from cus_app.supple.helper_functions import NULL_LIST, coerce_none

_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero
_COMBINE_DATETIME_FORMAT = "%b%d%Y%H:%M"

_FUNCTIONAL = [
    'multiobsid',
    'csrf_token',
    'template_time',
    'template_roll',
    'template_window',
    'submit_choice',
    'submit',
]

#: Edge case handling in processing form changes for flag-dependent divs, since the form will still have that information
_DITHER_PARAMS = [
    'dither_flag',
    'y_amp_asec',
    'y_freq_asec',
    'y_phase',
    'z_amp_asec',
    'z_freq_asec',
    'z_phase',
]

_TIME_PARAMS = [
    'window_constraint',
    'tstart',
    'tstop'
]

_ROLL_PARAMS = [
    'roll_constraint',
    'roll_180',
    'roll',
    'roll_tolerance'
]

_WINDOW_PARAMS = [
    'chip',
    'start_row',
    'start_column',
    'width',
    'height',
    'lower_threshold',
    'pha_range',
    'sample'
]

_FLAG_2_RANK = {
    'window_flag': 'time_ranks',
    'roll_flag': 'roll_ranks',
    'spwindow_flag': 'window_ranks',
}

_FLAG_2_COLUMN = {
    'window_flag': _TIME_PARAMS,
    'roll_flag': _ROLL_PARAMS,
    'spwindow_flag': _WINDOW_PARAMS
}

_SKIP_PARAM = _FUNCTIONAL + _TIME_PARAMS + _ROLL_PARAMS + _WINDOW_PARAMS + list(_FLAG_2_RANK.keys()) + list(_FLAG_2_RANK.values())


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

def convert_ra_dec_format(dra, ddec, oformat):
    """
    convert ra/dec format
    input:  dra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            ddec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
            oformat --- specify output format as either 'dd', or 'hmsdms'

    output: tra     --- either <hh>:<mm>:<ss> or <dd.ddddd> format
            tdec    --- either <dd>:<mm>:<ss> or <ddd.ddddd> format
    """
    #
    #--- Define input format
    #
    if ":" in str(ddec):
        iformat = 'hmsdms'
    else:
        iformat = 'dd'
    #
    #--- Switch formats
    #
    if iformat == 'dd' and oformat == 'hmsdms':
        angle_ra = Angle(f"{dra} degrees")
        tra = str(angle_ra.to_string(sep=":",pad=True,precision=4,unit='hourangle'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = str(angle_dec.to_string(sep=":",pad=True,precision=4,alwayssign=True,unit='degree'))
    elif iformat == 'hmsdms' and oformat == 'dd':
        angle_ra = Angle(f"{dra} hours")
        tra = float(angle_ra.to_string(decimal=True,precision=6,unit='degree'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = float(angle_dec.to_string(decimal=True,precision=6,unit='degree'))
    else:
        return dra, ddec
    
    return tra,tdec

def format_POST(ocat_form_dict):
    """
    Minor changes to listed form data after POST request and preparing ocat_form_dict
    """
    
    for k,v in ocat_form_dict.items():
        ocat_form_dict[k] = coerce_none(v)

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

def determine_changes(ocat_form_dict, ocat_data):
    """
    Iterate over select keys in the ocat_form_dict to identify revised parameters
    This generates the set of information used in filling out the Originals and Requests tables
    """
    #: Regular Changes
    change_dict = {}
    for key, new in ocat_form_dict.items():
        if key in _SKIP_PARAM:
            continue
        else:
            org = ocat_data.get(key)
            if not equal_values(org,new):
                    change_dict[key] = [org, new]
    #
    # --- Rank Changes (Handled Separately)
    # --- If flag changes, list that specifically and all ranks as changed
    #
    for flag in _FLAG_2_RANK.keys():
        new = ocat_form_dict.get(flag)
        org = ocat_data.get(flag)
        rank_list = _FLAG_2_RANK.get(flag)
        if org != new:
            change_dict[flag] = [org, new]
            change_dict[rank_list] = [ocat_data.get(rank_list), ocat_form_dict.get(rank_list)]
        elif not (org == 'N' and new == 'N'):
            #: Individual ranks possibly changed in instance where the selected ranks are
            change_dict = determine_changed_rank(change_dict, rank_list, ocat_data.get(rank_list), ocat_form_dict.get(rank_list))
    return change_dict


def determine_changed_rank(change_dict, rank_list, org, new):
    """
    Changes amongst individual ranks
    """
    change_list = []
    #: TODO check different sizes
    #: DOD, if same size, individual differences
    #: Special case when comparing time
    for org_rank, new_rank in zip(org, new):
        for key in new_rank.keys():
            pass
    return change_dict
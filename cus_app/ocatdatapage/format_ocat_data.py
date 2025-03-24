"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
from astropy.coordinates import Angle
import os
from datetime import datetime


_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"  #: NOTE Ocat dates are recorded without a leading zero. While datetime can process these dates, it never prints without a leading zero

_PULL_FORM_BY_CATEGORY = {
    "gen_param": [
        "seq_nbr",
        "status",
        "obsid",
        "proposal_number",
        "proposal_title",
        "obs_ao_str",
        "targname",
        "si_mode",
        "aca_mode",
        "instrument",
        "grating",
        "obs_type",
        "pi_name",
        "observer",
        "approved_exposure_time",
        "rem_exp_time",
        "proposal_join",
        "proposal_hst",
        "proposal_noao",
        "proposal_xmm",
        "proposal_vla",
        "proposal_vlba",
        "soe_st_sched_date",
        "lts_lt_plan",
        "planned_roll",
        "ra",
        "dec",
        "soe_roll",
        "y_det_offset",
        "z_det_offset",
        "trans_offset",
        "focus_offset",
        "raster_scan",
        "uninterrupt",
        "extend_src",
        "obj_flag",
        "object",
        "photometry_flag",
        "vmagnitude",
        "est_cnt_rate",
        "forder_cnt_rate",
    ],
    "dither_param": [
        "dither_flag",
        "y_amp",
        "y_freq",
        "y_phase",
        "z_amp",
        "z_freq",
        "z_phase"
    ],
    "time_param": [
        "window_flag",
        "time_ordr",
        "window_constraint"
    ],
    "other_param":[
        "constr_in_remarks",
        "pointing_constraint",
        "phase_constraint_flag",
        "phase_epoch",
        "phase_period",
        "phase_start",
        "phase_start_margin",
        "phase_end",
        "phase_end_margin",
        "group_id",
        "monitor_flag",
        "group_obsid",
        "monitor_series",
        "pre_id",
        "pre_min_lead",
        "pre_max_lead",
        "multitelescope",
        "observatories",
        "multitelescope_interval"
    ]
}
_NONE_FORM_EXCEPTIONS = ['dither_flag', 'window_flag'] #: list of parameters to include in form initialization even if they are None.

def format_for_form(ocat_data):
    form = {}
    #
    #--- Initialize form values which are direct fetches from the ocat_data
    #
    for category, parameter_list in _PULL_FORM_BY_CATEGORY.items():
        form[category] = {}
        for param in parameter_list:
            val = ocat_data.get(param)
            if (val is not None) or (param in _NONE_FORM_EXCEPTIONS):
                form[category][param] = val
    #
    #--- Initialize category specific form parameters
    form = general_additionals(form, ocat_data)
    form = dither_additionals(form,ocat_data)
    form = time_additionals(form, ocat_data)
    return form

def synchronize_values(form):
    #
    #--- Perform RA, DEC, and Dither conversions of the editable form values to change the non-editable versions
    #
    ra_hms = form.gen_param.ra_hms.data
    dec_dms = form.gen_param.dec_dms.data
    if ra_hms not in ('', None) and dec_dms not in ('', None):
        form.gen_param.ra.data, form.gen_param.dec.data = convert_ra_dec_format(ra_hms,dec_dms, oformat='dd')
    if form.dither_param.dither_flag.data == 'Y':
        form.dither_param.y_amp.data = convert_from_arcsec(form.dither_param.y_amp_asec.data)
        form.dither_param.y_freq.data = convert_from_arcsec(form.dither_param.y_freq_asec.data)
        form.dither_param.z_amp.data = convert_from_arcsec(form.dither_param.z_amp_asec.data)
        form.dither_param.z_freq.data = convert_from_arcsec(form.dither_param.z_freq_asec.data)
    return form
#
#--- General Category Functions
#
def general_additionals(form, ocat_data):
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
    form['gen_param']['rass'] = rass
    form['gen_param']['rosat'] = rosat
    form['gen_param']['dss'] = dss
    #
    #--- RA, Dec
    #
    ra = ocat_data.get('ra')
    dec = ocat_data.get('dec')
    if ra is not None and dec is not None:
        ra_hms, dec_dms = convert_ra_dec_format(ra, dec, 'hmsdms')
        form['gen_param']['ra_hms'] = ra_hms
        form['gen_param']['dec_dms'] = dec_dms
    
    #
    #--- Corrections
    #
    if form['gen_param'].get('rem_exp_time') < 0:
        form['gen_param']['rem_exp_time'] = 0.0

    return form

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
        tra = angle_ra.to_string(sep=":",pad=True,precision=4,unit='hourangle')
        angle_dec = Angle(f"{ddec} degrees")
        tdec = angle_dec.to_string(sep=":",pad=True,precision=4,alwayssign=True,unit='degree')
    elif iformat == 'hmsdms' and oformat == 'dd':
        angle_ra = Angle(f"{dra} hours")
        tra = float(angle_ra.to_string(decimal=True,precision=6,unit='degree'))
        angle_dec = Angle(f"{ddec} degrees")
        tdec = float(angle_dec.to_string(decimal=True,precision=6,unit='degree'))
    else:
        return dra, ddec
    
    return tra,tdec
#
#--- Dither Category Functions
#
def dither_additionals(form, ocat_data):
    keys = ('y_amp', 'y_freq', 'z_amp', 'z_freq')
    for key in keys:
        val = ocat_data.get(key)
        if val is not None:
            form['dither_param'][f'{key}_asec'] = convert_to_arcsec(ocat_data.get(key))
    return form

def convert_to_arcsec(degree):
    """convert degree value into arcsecs while retaining type

    :param degree: value in degrees
    :type degree: int, float, str
    :return: value in arcsecs
    :rtype: int, float, str
    """
    if isinstance(degree, float) or isinstance(degree, int):
        return round(degree * 3600,3)
    elif isinstance(degree,str):
        return str(round(float(degree)*3600,3))
    elif degree is None:
        return None

def convert_from_arcsec(arcsec):
    """convert arcsec value into degrees while retaining type

    :param arcsec: value in arcsecs
    :type arcsec: int, float, str
    :return: value in degrees
    :rtype: int, float, str
    """
    if isinstance(arcsec, float) or isinstance(arcsec, int):
        return round(arcsec / 3600,6)
    elif isinstance(arcsec,str):
        return str(round(float(arcsec)/3600, 6))
    elif arcsec is None:
        return None

#
#--- Time Constraint Functions
#
def time_additionals(form, ocat_data):
    if ocat_data.get("tstart") is not None:
        tstart = [datetime.strptime(x, _OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstart')]
        tstop = [datetime.strptime(x, _OCAT_DATETIME_FORMAT) for x in ocat_data.get('tstop')]
        
        form['time_param']['tstart_year'] = [dt.strftime("%Y") for dt in tstart]
        form['time_param']['tstop_year'] = [dt.strftime("%Y") for dt in tstop]
        
        form['time_param']['tstart_month'] = [dt.strftime("%b") for dt in tstart]
        form['time_param']['tstop_month'] = [dt.strftime("%b") for dt in tstop]
        
        form['time_param']['tstart_date'] = [dt.strftime("%d") for dt in tstart]
        form['time_param']['tstop_date'] = [dt.strftime("%d") for dt in tstop]
        
        form['time_param']['tstart_time'] = [dt.strftime("%H:%M") for dt in tstart]
        form['time_param']['tstop_time'] = [dt.strftime("%H:%M") for dt in tstop]
    return form
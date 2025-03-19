"""
**format_ocat_data.py**: Format ocat oriented data into Usint Form formats.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 18, 2025

"""
from astropy.coordinates import Angle
import os


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
        "approve_exposure_time",
        "rep_exp_time",
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
}
_NONE_FORM_EXCEPTIONS = ['dither_flag'] #: list of parameters to include in form initialization even if they are None.

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
    return form

def synchronize_values(form):
    #
    #--- Perform RA, DEC, and Dither conversions of the editable form values to change the non-editable versions
    #
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


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
        "remarks",
        "comments",
        "proposal_number",
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
    "roll_param": [
        "roll_flag",
        "roll_ordr",
        "roll_constraint",
        "roll_180",
        "roll",
        "roll_tolerance"
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
    ],
    "hrc_param": [
        "hrc_zero_block",
        "hrc_timing_mode",
        "hrc_si_mode"
    ],
    "acis_param": [
        "exp_mode",
        "bep_pack",
        "frame_time",
        "most_efficient",
        "dropped_chip_count",
        "ccdi0_on",
        "ccdi1_on",
        "ccdi2_on",
        "ccdi3_on",
        "ccds0_on",
        "ccds1_on",
        "ccds2_on",
        "ccds3_on",
        "ccds4_on",
        "ccds5_on",
        "subarray",
        "subarray_start_row",
        "subarray_row_count",
        "duty_cycle",
        "secondary_exp_count",
        "primary_exp_time",
        "onchip_sum",
        "onchip_row_count",
        "onchip_column_count",
        "eventfilter",
        "eventfilter_lower",
        "eventfilter_higher",
        "multiple_spectral_lines",
        "spectra_max_count",
    ],
    "aciswin_param": [
        'spwindow_flag',
        'aciswin_no',
        'chip',
        'start_row',
        'start_column',
        'height',
        'width',
        'lower_threshold',
        'pha_range',
        'sample'
        ],
    "too_param": [
        'tooid',
        'too_trig',
        'too_type',
        'too_start',
        'too_stop',
        'too_followup',
        'too_remarks'
        ]
}
_NONE_FORM_EXCEPTIONS = ['dither_flag', 'window_flag', 'spwindow_flag'] #: list of parameters to include in form initialization even if they are None.

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
#--- Time Category Functions
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
#
#--- Roll Category Functions
#
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
#
#--- Window Category Functions
#
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

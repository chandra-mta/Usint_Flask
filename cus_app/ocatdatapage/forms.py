"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 20.025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import Field, SelectField, StringField, SubmitField, FormField, FloatField, IntegerField, FieldList, HiddenField
from wtforms.validators import ValidationError, DataRequired
from datetime import datetime
from calendar import month_abbr


#
#---- Common Choice of Pulldown Fields
#
_CHOICE_NNPY = ((None, 'NA'), ('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'),)
_CHOICE_NY   = (('N','NO'), ('Y','YES'),)
_CHOICE_NNY  = ((None, 'NA'), ('N', 'NO'), ('Y', 'YES'),)
_CHOICE_CP   = (('Y','CONSTRAINT'),('P','PREFERENCE'),)
_CHOICE_NNPC = ((None,'NA'),('N','NO'), ('P','PREFERENCE'), ('Y', 'CONSTRAINT'),)

#
#--- Time Selectors
#
_YEAR_LIST = [str(x + datetime.now().year) for x in range(-3,5)]
_YEAR_CHOICE = [(None,'NA')] + [(x,x) for x in _YEAR_LIST]
_MONTH_CHOICE = [(None,'NA')] + [(x,x) for x in month_abbr[1:]]
_DAY_LIST = [f"{x:02}" for x in range(1,32)]
_DAY_CHOICE = [(None,'NA')] + [(x,x) for x in _DAY_LIST]

_USINT_DATETIME_FORMAT = "%b-%d-%Y %H:%M"
_NONEDIT = {'readonly': True}

"""
**CONCEPT MEMO**: All of the variable and function names within the form classes follow specific FlaskForm criteria in order to
allow for Jinja Template page generation to input initial data into the Ocat Form using the data argument, as well as validate
input selections for fields with the validate_<field name> functions. Changing these names will break the form validation unless matched with corresponding
initial data dictionary keys and field names.
"""

def coerce_none(value):
    #: Apply as coerce argument to any field to cast None to correct data type
    if value == 'None':
        return None
    return value

class GeneralParamForm(FlaskForm):
    seq_nbr = IntegerField("Sequence Number", render_kw=_NONEDIT)
    status = StringField("Status", render_kw=_NONEDIT)
    obsid = IntegerField("Obsid", render_kw=_NONEDIT)
    proposal_number = IntegerField("Proposal Number", render_kw=_NONEDIT)
    proposal_title = StringField("Proposal Title", render_kw=_NONEDIT)
    obs_ao_str = StringField("Obs AO Status", render_kw=_NONEDIT)

    targname = StringField("Target Name", validators=[DataRequired()])
    si_mode = StringField("SI Mode", render_kw=_NONEDIT)
    aca_mode = StringField("ACA Mode", render_kw=_NONEDIT)

    choice = ("ACIS-I", "ACIS-S", "HRC-I", "HRC-S")
    instrument = SelectField("Instrument", choices=[(x, x) for x in choice])
    choice = (None, "LETG", "HETG")
    grating = SelectField("Grating", choices=[(x, x) for x in choice])
    choice = ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')
    obs_type = SelectField("Type", choices=[(x, x) for x in choice])

    pi_name = StringField("PI Name", render_kw=_NONEDIT)
    observer = StringField("Observer", render_kw=_NONEDIT)
    approved_exposure_time = StringField("Exposure Time", render_kw=_NONEDIT)
    rem_exp_time = StringField("Remaining Exposure Time", render_kw=_NONEDIT)

    proposal_joint = StringField("Joint Proposal", render_kw=_NONEDIT)
    proposal_hst = StringField("HST Approved Time", render_kw=_NONEDIT)
    proposal_noao = StringField("NOAO Approved Time", render_kw=_NONEDIT)
    proposal_xmm = StringField("XMM Approved Time", render_kw=_NONEDIT)
    proposal_rxte = StringField("RXTE Approved Time", render_kw=_NONEDIT)
    proposal_vla = StringField("VLA Approved Time", render_kw=_NONEDIT)
    proposal_vlba = StringField("VLBA Approved Time", render_kw=_NONEDIT)

    soe_st_sched_date = StringField("Scheduled Date", render_kw=_NONEDIT)
    lts_lt_plan = StringField("LST Date", render_kw=_NONEDIT)

    rass = StringField("RASS", render_kw=_NONEDIT)
    rosat = StringField("ROSAT", render_kw=_NONEDIT)
    dss = StringField("DSS", render_kw=_NONEDIT)

    ra_hms = StringField("RA (HMS)", default='00:00:00.0000')
    dec_dms = StringField("Dec (DMS)", default='+00:00:00.0000')
    planned_roll = StringField("Planned Roll", render_kw=_NONEDIT)
    ra = FloatField("RA",default = 0.0, render_kw=_NONEDIT)
    dec = FloatField("Dec",default = 0.0, render_kw=_NONEDIT)
    soe_roll = StringField("Roll Observed", render_kw=_NONEDIT)

    y_det_offset = StringField("Offset Y")
    z_det_offset = StringField("Offset Z")
    trans_offset = StringField("Z-Sim")
    focus_offset = StringField("Sim-Focus")
    raster_scan = StringField("Raster Scan", render_kw=_NONEDIT)

    uninterrupt = SelectField("Uninterrupted Obs", choices=_CHOICE_NNPY)
    extended_src = SelectField("Extended SRC", choices=_CHOICE_NY)
    obj_flag = SelectField("Solar System Object", choices=[(x, x) for x in ('NO', 'MT', 'SS')])
    object = SelectField("Object", choices=[(x, x) for x in (None, 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')])
    photometry_flag = SelectField("Photometry", choices=_CHOICE_NNY)
    vmagnitude = StringField("V Mag")
    est_cnt_rate = StringField("Count Rate")
    forder_cnt_rate = StringField("1st Order Rate")

class DitherParamForm(FlaskForm):
    dither_flag = SelectField("Dither",  choices=_CHOICE_NNY)
    
    y_amp_asec = FloatField("Y_Amp (in arcsec)", default = 0.0)
    y_freq_asec = FloatField("Y_Freq (in arcsec/sec)", default = 0.0)
    y_phase = FloatField("Y_Phase", default = 0.0)
    
    y_amp = FloatField("Y_Amp (in degrees)", default = 0.0, render_kw=_NONEDIT)
    y_freq = FloatField("Y_Freq (in degrees/sec)", default = 0.0, render_kw=_NONEDIT)

    z_amp_asec = FloatField("Z_Amp (in arcsec)", default = 0.0)
    z_freq_asec = FloatField("Z_Freq (in arcsec/sec)", default = 0.0)
    z_phase = FloatField("Z_Phase", default = 0.0)
    
    z_amp = FloatField("Z_Amp (in degrees)", default = 0.0, render_kw=_NONEDIT)
    z_freq = FloatField("Z_Freq (in degrees/sec)", default = 0.0, render_kw=_NONEDIT)

class TimeParamForm(FlaskForm):
    window_flag = HiddenField("Window Flag") #: Hidden as this can change in the form but indirectly.
    time_ordr = HiddenField("Rank") #: Hidden as this can change in the form but indirectly.
    window_constraint = FieldList(SelectField("Window Constraint",choices=_CHOICE_NNPC))
    tstart = FieldList(HiddenField("Start"))
    tstop = FieldList(HiddenField("Stop"))

    tstart_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")
    tstop_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")

    tstart_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")
    tstop_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")

    tstart_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Day")
    tstop_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Year")
    #: TODO include validators for time
    tstart_time = FieldList(StringField("Time", default= "00:00"),label="Time (24hr)")
    tstop_time = FieldList(StringField("Time", default= "00:00"),label="Time (24hr)")

class OtherParamForm(FlaskForm):
    constr_in_remarks = SelectField("Constraint in Remarks?", choices=_CHOICE_NNPY)
    pointing_constraint = SelectField("Pointing Update", choices=_CHOICE_NNY)

    phase_constraint_flag = SelectField("Phase Constraint", choices=_CHOICE_NNPC, render_kw=_NONEDIT)
    phase_epoch = FloatField("Phase Epoch")
    phase_period = FloatField("Phase Period")
    phase_start = FloatField("Phase Min")
    phase_start_margin = FloatField("Phase Min Error")
    phase_end = FloatField("Phase Max")
    phase_end_margin = FloatField("Phase Max Error")

    group_id = StringField("Group ID", render_kw=_NONEDIT)
    monitor_flag = SelectField("Monitoring Observation", choices=_CHOICE_NY)
    group_obsid = FieldList(IntegerField(render_kw=_NONEDIT), label="Remaining Observations in the Group")
    monitor_series = FieldList(IntegerField(render_kw=_NONEDIT), label="Remaining Observations in the Monitoring")
    pre_id = IntegerField("Follows ObsID#")
    pre_min_lead = FloatField("Follows Obs Min Int")
    pre_max_lead = FloatField("Follows Obs Max Int")

    multitelescope = SelectField("Coordinated Observation", choices=_CHOICE_NNPY)
    observatories = StringField("Observatories")
    multitelescope_interval = StringField("Max Coordination Offset")

class OcatParamForm(FlaskForm):
    """
    Extension of FlaskForm for Ocat Parameter Data Page Form.
    Includes all parameters with corresponding editable fields.
    Note that this means non-editable information is rendered directly by flask template and not by form method.
    """
    gen_param = FormField(GeneralParamForm)
    dither_param = FormField(DitherParamForm)
    time_param = FormField(TimeParamForm)
    other_param = FormField(OtherParamForm)
    
    open_dither = SubmitField("Open Dither")
    open_time = SubmitField("Open Time")
    refresh = SubmitField("Refresh")
    submit = SubmitField("Submit")
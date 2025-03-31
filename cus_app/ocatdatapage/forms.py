"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 20.025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, FormField, FloatField, IntegerField, FieldList, HiddenField, TextAreaField, RadioField
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
_CHOICE_EVENT = ((None, "NA"),("F","F"),("VF","VF"),("F+B","F+B"),("G","G"))
_CHOICE_CHIP = [('N','NO'), ('Y','YES'), ('O1','OPT1'),('O2','OPT2'), ('O3', 'OPT3'), ('O4','OPT4'), ('O5','OPT5')]
_CHOICE_WINDOW = [(None,'NA')] + [(x, x) for x in ('I0', 'I1',  'I2', 'I3', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5')]
_CHOICE_SUBMIT = [("norm", "Normal Change"),
                ("asis","Observation is Approved for flight"),
                ("remove","ObsID no longer ready to go"),
                ("clone","Split this ObsID")
            ]

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

    remarks = TextAreaField("Remarks", default = '')
    comments = TextAreaField("Comments", default = '')
    proposal_number = StringField("Proposal Number", render_kw=_NONEDIT)

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
    window_constraint = FieldList(SelectField("Window Constraint",choices=_CHOICE_NNPC), label = "Window Constraint")

    tstart_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")
    tstop_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")

    tstart_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")
    tstop_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")

    tstart_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Day")
    tstop_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Year")
    #: TODO include validators for time
    tstart_time = FieldList(StringField("Time", default= "00:00"),label="Time (24hr)")
    tstop_time = FieldList(StringField("Time", default= "00:00"),label="Time (24hr)")

    add_time = SubmitField("Add Time Rank")
    remove_time = SubmitField("Remove NA Time Entry")

class RollParamForm(FlaskForm):
    roll_flag = HiddenField("Roll Flag") #: Hidden as this can change in the form but indirectly.
    roll_ordr = HiddenField("Rank") #: Hidden as this can change in the form but indirectly.
    roll_constraint = FieldList(SelectField("Type of Constraint",choices=_CHOICE_NNPC), label = "Type of Constraint")
    roll_180 = FieldList(SelectField("Roll 180?",choices=_CHOICE_NNY), label = "Roll 180?")
    roll = FieldList(StringField("Roll"), label = "Roll")
    roll_tolerance = FieldList(StringField("Roll Tolerance"), label = "Roll Tolerance")

    add_roll = SubmitField("Add Roll Rank")
    remove_roll = SubmitField("Remove NA Roll Entry")

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

class HRCParamForm(FlaskForm):
    hrc_timing_mode = SelectField("HRC Timing Mode", choices=_CHOICE_NY)
    hrc_zero_block = SelectField("Zero Block", choices=_CHOICE_NY)
    hrc_si_mode = StringField("SI Mode")

class ACISParamForm(FlaskForm):
    exp_mode = SelectField("Acis Exposure Mode", choices=((None,"NA"),("TE","TE"),("CC","CC")))
    bep_pack = SelectField("Event TM Format", choices = _CHOICE_EVENT)
    frame_time = StringField("Frame Time")
    most_efficient = SelectField("Most Efficient", choices = _CHOICE_NNY)
    dropped_chip_count = StringField("Dropped Chip Count", render_kw=_NONEDIT)
    ccdi0_on = SelectField("I0", choices=_CHOICE_CHIP)
    ccdi1_on = SelectField("I1", choices=_CHOICE_CHIP)
    ccdi2_on = SelectField("I2", choices=_CHOICE_CHIP)
    ccdi3_on = SelectField("I3", choices=_CHOICE_CHIP)
    ccds0_on = SelectField("SO", choices=_CHOICE_CHIP)
    ccds1_on = SelectField("S1", choices=_CHOICE_CHIP)
    ccds2_on = SelectField("S2", choices=_CHOICE_CHIP)
    ccds3_on = SelectField("S3", choices=_CHOICE_CHIP)
    ccds4_on = SelectField("S4", choices=_CHOICE_CHIP)
    ccds5_on = SelectField("S5", choices=_CHOICE_CHIP)
    subarray = SelectField("Use Subarray", choices=[("NONE", "NONE"), ("N", "NO"), ("CUSTOM", "YES")])
    subarray_start_row = StringField("Start")
    subarray_row_count = StringField("Rows")
    duty_cycle = SelectField("Duty Cycle", choices=_CHOICE_NNY)
    secondary_exp_count = StringField("Number")
    primary_exp_time = StringField("Tprimary")
    onchip_sum = SelectField("Onchip Summing", choices=_CHOICE_NNY)
    onchip_row_count = IntegerField("Onchip Rows")
    onchip_column_count = IntegerField("Onchip Columns")
    eventfilter = SelectField("Energy Filter", choices=_CHOICE_NNY)
    eventfilter_lower = StringField("Lowest Energy")
    eventfilter_higher = StringField("Energy Range")
    multiple_spectral_lines = SelectField("Multi Spectral Lines", choices=_CHOICE_NNY)
    spectra_max_count = StringField("Spectra Max Count")

class ACISWinParamForm(FlaskForm):
    spwindow_flag = HiddenField("Window Flag") #: Hidden as this can change in the form but indirectly.
    aciswin_no = HiddenField("Rank") #: Hidden as this can change in the form but indirectly.
    chip = FieldList(SelectField("Chip",choices=_CHOICE_WINDOW), label = "Chip")
    start_row = FieldList(StringField("Start Row"), label = "Start Row")
    start_column = FieldList(StringField("Start Column"), label = "Start Column")
    height = FieldList(StringField("Height"), label = "Height")
    width = FieldList(StringField("Width"), label = "Width")
    lower_threshold = FieldList(StringField("Lowest Energy"), label = "Lowest Energy")
    pha_range = FieldList(StringField("Energy Range"), label = "Energy Range")
    sample = FieldList(StringField("Sample Rate"), label = "Sample Rate")

    add_window = SubmitField("Add Window Rank")
    remove_window = SubmitField("Remove NA Window Entry")

class TOOParamForm(FlaskForm):
    tooid = StringField("TOO ID", render_kw=_NONEDIT)
    too_trig = StringField("TOO Trigger", render_kw=_NONEDIT)
    too_type = StringField("TOO Type", render_kw=_NONEDIT)
    too_start = StringField("TOO Start", render_kw=_NONEDIT)
    too_stop = StringField("TOO Stop", render_kw=_NONEDIT)
    too_followup = StringField("# of Follow-up Observations", render_kw=_NONEDIT)
    too_remarks = StringField("TOO Remarks", render_kw=_NONEDIT)


class OcatParamForm(FlaskForm):
    """
    Extension of FlaskForm for Ocat Parameter Data Page Form.
    Includes all parameters with corresponding editable fields.
    Note that this means non-editable information is rendered directly by flask template and not by form method.
    """
    gen_param = FormField(GeneralParamForm)
    dither_param = FormField(DitherParamForm)
    time_param = FormField(TimeParamForm)
    roll_param = FormField(RollParamForm)
    other_param = FormField(OtherParamForm)
    hrc_param = FormField(HRCParamForm)
    acis_param = FormField(ACISParamForm)
    aciswin_param = FormField(ACISWinParamForm)
    too_param = FormField(TOOParamForm)
    
    open_dither = SubmitField("Open Dither")
    open_time = SubmitField("Open Time")
    open_roll = SubmitField("Open Roll")
    open_aciswin = SubmitField("Open Window")
    refresh = SubmitField("Refresh")
    submit_choice = RadioField("Submit Options", choices=_CHOICE_SUBMIT)
    multiobsid = StringField("Multi-Obsid")
    submit = SubmitField("Submit")
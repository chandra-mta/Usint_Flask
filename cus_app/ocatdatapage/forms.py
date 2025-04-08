"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import Field, Form, SelectField, StringField, SubmitField, FormField, FloatField, IntegerField, FieldList, HiddenField, TextAreaField, RadioField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, NumberRange
from wtforms.widgets import Input
from datetime import datetime
from calendar import month_abbr
import json


#
#---- Common Choice of Pulldown Fields
#
_CHOICE_CP   = (('Y','CONSTRAINT'),('P','PREFERENCE'),)
_CHOICE_DITHER = [('N', 'NO', {"id": "closeDither"}), ('Y', 'YES',{"id": "openDither"} )]
_CHOICE_WINDOW = [('N', 'NO', {"id": "closeWindow"}), ('Y', 'YES',{"id": "openWindow"} )]
_CHOICE_ROLL = [('N', 'NO', {"id": "closeRoll"}), ('Y', 'YES',{"id": "openRoll"} )]
_CHOICE_INSTRUMENT = (
        ("ACIS-I", "ACIS-I", {"id":"switchACIS"}),
        ("ACIS-S", "ACIS-S", {"id":"switchACIS"}),
        ("HRC-I", "HRC-I", {"id":"switchHRC"}),
        ("HRC-S", "HRC-S", {"id":"switchHRC"}),
    )

_CHOICE_NY   = (('N','NO'), ('Y','YES'))
_CHOICE_NPY = (('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'))
_CHOICE_NNY  = ((None, 'NA'), ('N', 'NO'), ('Y', 'YES'))

_CHOICE_NNPY = ((None, 'NA'), ('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'),)

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
_OCAT_DATETIME_FORMAT = "%b %d %Y %I:%M%p"
_USINT_DATETIME_FORMAT = "%b %d %Y %H:%M"

_DATETIME_FORMATS = [_USINT_DATETIME_FORMAT, _OCAT_DATETIME_FORMAT, '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']

"""
**CONCEPT MEMO**: All of the variable and function names within the form classes follow specific FlaskForm criteria in order to
allow for Jinja Template page generation to input initial data into the Ocat Form using the data argument, as well as validate
input selections for fields with the validate_<field name> functions. Changing these names will break the form validation unless matched with corresponding
initial data dictionary keys and field names.
"""
with open('../static/labels.json') as f:
    _LABELS = json.load(f)
with open('../static/defaults.json') as f:
    _DEFAULTS = json.load(f)

class ButtonWidget(Input):
    input_type='button'
    validation_attrs = ['required', 'disabled']
    def __call__(self, field, **kwargs):
        kwargs.setdefault("value", field.label.text)
        if field.onclick is not None:
            kwargs.setdefault("onclick", field.onclick)
        return super().__call__(field, **kwargs)

class ButtonField(Field):
    widget = ButtonWidget()

    def __init__(self, label=None, validators=None, onclick=None, **kwargs):
        self.onclick = onclick
        super().__init__(label=None, validators=None,**kwargs)

class TimeRankDateTimeField(DateTimeField):
    def process_data(self, value):
        if isinstance(value, str):
            d_value = None
            for format in self.format:
                try:
                    # Custom processing: parse the string into a datetime object
                    d_value = datetime.strptime(value, format)
                    break
                except ValueError:
                    pass
            self.data = d_value
        else:
            super().process_data(value)

class TimeRank(Form):
    window_constraint = SelectField(_LABELS.get('window_constraint'), choices=_CHOICE_CP)
    tstart = TimeRankDateTimeField(_LABELS.get('tstart'), format=_DATETIME_FORMATS, default=datetime.now())
    tstop = TimeRankDateTimeField(_LABELS.get('tstop'), format=_DATETIME_FORMATS, default=datetime.now())
    remove_rank = ButtonField(_LABELS.get('remove_rank'), render_kw={'class':'removeRow'})

class RollRank(Form):
    roll_constraint = SelectField(_LABELS.get('roll_constraint'),choices=_CHOICE_CP)
    roll_180 = SelectField(_LABELS.get('roll_180'),choices=_CHOICE_NNY)
    roll = FloatField(_LABELS.get('roll'), validators=[NumberRange(min=0, max=360)])
    roll_tolerance = FloatField(_LABELS.get('roll_tolerance'), validators=[NumberRange(min=0, max=360)])
    remove_rank = ButtonField(_LABELS.get('remove_rank'), render_kw={'class':'removeRow'})

class OcatParamForm(FlaskForm):
    #
    # --- General
    #
    targname = StringField(_LABELS.get('targname'), validators=[DataRequired()])
    instrument = SelectField(_LABELS.get('instrument'), choices=_CHOICE_INSTRUMENT, validators=[DataRequired()])

    choices = [(x, x) for x in (None, "LETG", "HETG")]
    grating = SelectField(_LABELS.get('grating'), choices=choices)

    choices = [(x, x) for x in ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')]
    obs_type = SelectField(_LABELS.get('obs_type'), choices=choices)

    ra_hms = StringField(_LABELS.get('ra_hms'), default=_DEFAULTS.get('ra_hms')) #: TODO make Javascript dynamically change RA, DEC display
    dec_dms = StringField(_LABELS.get('dec_dms'), default=_DEFAULTS.get('dec_dms'))

    y_det_offset = FloatField(_LABELS.get('y_det_offset'), validators=[NumberRange(min=-120.0, max=120.0)])
    z_det_offset = FloatField(_LABELS.get('z_det_offset'), validators=[NumberRange(min=-120.0, max=120.0)])
    trans_offset = FloatField(_LABELS.get('trans_offset'), validators=[NumberRange(min=-190.5, max=126.621)])
    focus_offset = FloatField(_LABELS.get('focus_offset'))

    uninterrupt = SelectField(_LABELS.get('uninterrupt'), choices=_CHOICE_NPY)
    extended_src = SelectField(_LABELS.get('extended_src'), choices=_CHOICE_NY)
    obj_flag = SelectField(_LABELS.get('obj_flag'), choices=[(x, x) for x in ('NO', 'MT', 'SS')])

    choices = [(x, x) for x in ('NONE', 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')]
    object = SelectField(_LABELS.get('object'), choices=choices)
    photometry_flag = SelectField(_LABELS.get('photometry_flag'), choices=_CHOICE_NY)
    vmagnitude = FloatField(_LABELS.get('vmagnitude'), validators=[NumberRange(min=-15, max=20)])
    est_cnt_rate = FloatField(_LABELS.get('est_cnt_rate'), validators=[DataRequired(), NumberRange(min=0, max=100000)])
    forder_cnt_rate = FloatField(_LABELS.get('forder_cnt_rate'), validators=[NumberRange(min=0, max=100000)]) #: Required if grating is not none, TODO find validator

    remarks = TextAreaField(_LABELS.get('remarks'), default = '')
    comments = TextAreaField(_LABELS.get('comments'), default = '')
    #
    # --- Dither
    #
    dither_flag = SelectField(_LABELS.get('dither_flag'),  choices=_CHOICE_DITHER)
    y_amp_asec = FloatField(_LABELS.get('y_amp_asec'))
    y_freq_asec = FloatField(_LABELS.get('y_freq_asec'))
    y_phase = FloatField(_LABELS.get('y_phase'))
    z_amp_asec = FloatField(_LABELS.get('z_amp_asec'))
    z_freq_asec = FloatField(_LABELS.get('z_freq_asec'))
    z_phase = FloatField(_LABELS.get('z_phase'))
    #
    # --- Time 
    #
    window_flag = SelectField(_LABELS.get('window_flag'),  choices=_CHOICE_WINDOW) #: Cast to and from P value depending on window_constraints
    time_ranks = FieldList(FormField(TimeRank,label=_LABELS.get('time_ranks')))
    #
    # --- Roll
    #
    roll_flag = SelectField(_LABELS.get('roll_flag'), choices=_CHOICE_ROLL) #: Cast to and from P value depending on roll_constraints
    roll_ranks = FieldList(FormField(RollRank, label=_LABELS.get('roll_ranks')))
    #
    # --- Other (Phase)
    #
    constr_in_remarks = SelectField(_LABELS.get('constr_in_remarks'), choices=_CHOICE_NPY)
    pointing_constraint = SelectField(_LABELS.get('pointing_constraint'), choices=_CHOICE_NNY)
    phase_epoch = FloatField(_LABELS.get('phase_epoch'), validators=[NumberRange(min=46066.0)])
    phase_period = FloatField(_LABELS.get('phase_period'))
    phase_start = FloatField(_LABELS.get('phase_start'), validators=[NumberRange(min=0, max=1)])
    phase_start_margin = FloatField(_LABELS.get('phase_start_margin'), validators=[NumberRange(min=0, max=0.5)])
    phase_end = FloatField(_LABELS.get('phase_end'), validators=[NumberRange(min=0, max=1)])
    phase_end_margin = FloatField(_LABELS.get('phase_end_margin'), validators=[NumberRange(min=0, max=0.5)])
    #
    # --- Other (Group)
    #
    monitor_flag = SelectField(_LABELS.get('monitor_flag'), choices=_CHOICE_NY)
    pre_id = IntegerField(_LABELS.get('pre_id'))
    pre_min_lead = FloatField(_LABELS.get('pre_min_lead'), validators=[NumberRange(min=0, max=364)])
    pre_max_lead = FloatField(_LABELS.get('pre_max_lead'), validators=[NumberRange(min=0.01, max=365)])
    #
    # --- Other (Joint)
    #
    multitelescope = SelectField(_LABELS.get('multitelescope'), choices=_CHOICE_NPY)
    observatories = StringField(_LABELS.get('observatories'))
    multitelescope_interval = FloatField(_LABELS.get('multitelescope_interval'))
    #
    # -- HRC
    #
    hrc_timing_mode = SelectField(_LABELS.get('hrc_timing_mode'), choices=_CHOICE_NY)
    hrc_zero_block = SelectField(_LABELS.get('hrc_zero_block'), choices=_CHOICE_NY)
    hrc_si_mode = StringField(_LABELS.get('hrc_si_mode'))

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

class ConfirmForm(FlaskForm):
    """
    Extension of FlaskForm for the parameter change confirmation page.
    """
    previous_page = SubmitField("Previous Page")
    finalize = SubmitField("Finalize")

"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

**CONCEPT MEMO**: All of the variable and function names within the form classes follow specific FlaskForm criteria in order to
allow for Jinja Template page generation to input initial data into the Ocat Form using the data argument, as well as validate
input selections for fields with the validate_<field name> functions. Changing these names will break the form validation unless matched with corresponding
initial data dictionary keys and field names.

"""
from flask_wtf import FlaskForm
from wtforms import Field, Form, SelectField, StringField, SubmitField, FormField, FloatField, IntegerField, FieldList, TextAreaField, RadioField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.widgets import Input
from datetime import datetime
import json
import os
from cus_app.supple.helper_functions import DATETIME_FORMATS

#
#---- Common Choice of Pulldown Fields
#
_CHOICE_INSTRUMENT = [(x,x) for x in ('ACIS-I', 'ACIS-S', 'HRC-I', 'HRC-S')]

_CHOICE_EVENT = ((None, "NA"),("F","F"),("VF","VF"),("F+B","F+B"),("G","G"))
_CHOICE_CHIP = [(None, "NA"),('N','NO'), ('Y','YES'), ('O1','OPT1'),('O2','OPT2'), ('O3', 'OPT3'), ('O4','OPT4'), ('O5','OPT5')]
_CHOICE_WINDOW_CHIP = [(None,'NA')] + [(x, x) for x in ('I0', 'I1',  'I2', 'I3', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5')]
_CHOICE_SUBARRAY = [(None, "NA"), ("CUSTOM", "CUSTOM")]

_CHOICE_NY   = (('N','NO'), ('Y','YES'))
_CHOICE_NPY = (('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'))
_CHOICE_NNY  = ((None, 'NA'), ('N', 'NO'), ('Y', 'YES'))
_CHOICE_CP   = (('Y','CONSTRAINT'),('P','PREFERENCE'),)

_CHOICE_SUBMIT = [("norm", "Normal Change"),
                ("asis","Observation is Approved for flight"),
                ("remove","ObsID no longer ready to go"),
                ("clone","Split this ObsID")
            ]
stat_dir =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'static')
with open(os.path.join(stat_dir, 'labels.json')) as f:
    _LABELS = json.load(f)

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
    window_constraint = SelectField(_LABELS.get('window_constraint'), choices=_CHOICE_CP, default='Y')
    tstart = TimeRankDateTimeField(_LABELS.get('tstart'), format=DATETIME_FORMATS, default=datetime.now())
    tstop = TimeRankDateTimeField(_LABELS.get('tstop'), format=DATETIME_FORMATS, default=datetime.now())
    remove_rank = ButtonField(_LABELS.get('remove_rank'), render_kw={'class':'removeRow'})

class RollRank(Form):
    roll_constraint = SelectField(_LABELS.get('roll_constraint'),choices=_CHOICE_CP, default='Y')
    roll_180 = SelectField(_LABELS.get('roll_180'),choices=_CHOICE_NNY, default = 'N')
    roll = FloatField(_LABELS.get('roll'), validators=[Optional(),NumberRange(min=0, max=360)], default = 0.0)
    roll_tolerance = FloatField(_LABELS.get('roll_tolerance'), validators=[Optional(),NumberRange(min=0, max=360)], default = 0.0)
    remove_rank = ButtonField(_LABELS.get('remove_rank'), render_kw={'class':'removeRow'})

class WindowRank(Form):
    chip = SelectField(_LABELS.get('chip'),choices=_CHOICE_WINDOW_CHIP, default='I0')
    start_row = IntegerField(_LABELS.get('start_row'), validators=[Optional(),NumberRange(min=1,max=1024)], default = 1)
    start_column = IntegerField(_LABELS.get('start_column'), validators=[Optional(),NumberRange(min=1,max=1024)], default = 1)
    width = IntegerField(_LABELS.get('width'), validators=[Optional(),NumberRange(min=1,max=1024)], default = 1023)
    height = IntegerField(_LABELS.get('height'), validators=[Optional(),NumberRange(min=1,max=1024)], default = 1023)

    lower_threshold = FloatField(_LABELS.get('lower_threshold'), validators=[Optional(),NumberRange(min=0,max=15)], default= 0.08)
    pha_range = FloatField(_LABELS.get('pha_range'), validators=[Optional(),NumberRange(min=0,max=15)], default = 13.0)
    sample = IntegerField(_LABELS.get('sample'), validators=[Optional(),NumberRange(min=0,max=255)], default = 0)
    remove_rank = ButtonField(_LABELS.get('remove_rank'), render_kw={'class':'removeRow'})

class OcatParamForm(FlaskForm):
    #
    # --- General
    #
    targname = StringField(_LABELS.get('targname'), validators=[DataRequired()])
    instrument = SelectField(_LABELS.get('instrument'), choices=_CHOICE_INSTRUMENT)

    choices = [(x, x) for x in (None, "LETG", "HETG")]
    grating = SelectField(_LABELS.get('grating'), choices=choices)

    choices = [(x, x) for x in ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')]
    obs_type = SelectField(_LABELS.get('obs_type'), choices=choices)

    ra_hms = StringField(_LABELS.get('ra_hms'), default="00:00:00.0000") #: TODO make Javascript dynamically change RA, DEC display
    dec_dms = StringField(_LABELS.get('dec_dms'), default="+00:00:00.0000")

    y_det_offset = FloatField(_LABELS.get('y_det_offset'), validators=[Optional(),NumberRange(min=-120.0, max=120.0)])
    z_det_offset = FloatField(_LABELS.get('z_det_offset'), validators=[Optional(),NumberRange(min=-120.0, max=120.0)])
    trans_offset = FloatField(_LABELS.get('trans_offset'), validators=[Optional(),NumberRange(min=-190.5, max=126.621)])
    focus_offset = FloatField(_LABELS.get('focus_offset'), validators=[Optional()])

    uninterrupt = SelectField(_LABELS.get('uninterrupt'), choices=_CHOICE_NPY)
    extended_src = SelectField(_LABELS.get('extended_src'), choices=_CHOICE_NY)
    obj_flag = SelectField(_LABELS.get('obj_flag'), choices=[(x, x) for x in ('NO', 'MT', 'SS')])

    choices = [(x, x) for x in ('NONE', 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')]
    object = SelectField(_LABELS.get('object'), choices=choices)
    photometry_flag = SelectField(_LABELS.get('photometry_flag'), choices=_CHOICE_NY)
    vmagnitude = FloatField(_LABELS.get('vmagnitude'), validators=[Optional(),NumberRange(min=-15, max=20)])
    est_cnt_rate = FloatField(_LABELS.get('est_cnt_rate'), validators=[Optional(),NumberRange(min=0, max=100000)])
    forder_cnt_rate = FloatField(_LABELS.get('forder_cnt_rate'), validators=[Optional(),NumberRange(min=0, max=100000)]) #: Required if grating is not none, TODO find validator

    remarks = TextAreaField(_LABELS.get('remarks'), validators=[Optional()])
    comments = TextAreaField(_LABELS.get('comments'), validators=[Optional()])
    #
    # --- Dither
    #
    dither_flag = SelectField(_LABELS.get('dither_flag'),  choices=_CHOICE_NY)
    y_amp_asec = FloatField(_LABELS.get('y_amp_asec'), validators=[Optional()])
    y_freq_asec = FloatField(_LABELS.get('y_freq_asec'), validators=[Optional()])
    y_phase = FloatField(_LABELS.get('y_phase'), validators=[Optional()])
    z_amp_asec = FloatField(_LABELS.get('z_amp_asec'), validators=[Optional()])
    z_freq_asec = FloatField(_LABELS.get('z_freq_asec'), validators=[Optional()])
    z_phase = FloatField(_LABELS.get('z_phase'), validators=[Optional()])
    #
    # --- Time 
    #
    window_flag = SelectField(_LABELS.get('window_flag'),  choices=_CHOICE_NY) #: Cast to and from P value depending on window_constraints
    time_ranks = FieldList(FormField(TimeRank,label=_LABELS.get('time_ranks')))
    #
    # --- Roll
    #
    roll_flag = SelectField(_LABELS.get('roll_flag'), choices=_CHOICE_NY) #: Cast to and from P value depending on roll_constraints
    roll_ranks = FieldList(FormField(RollRank, label=_LABELS.get('roll_ranks')))
    #
    # --- Other (Phase)
    #
    constr_in_remarks = SelectField(_LABELS.get('constr_in_remarks'), choices=_CHOICE_NPY)
    pointing_constraint = SelectField(_LABELS.get('pointing_constraint'), choices=_CHOICE_NNY)
    phase_epoch = FloatField(_LABELS.get('phase_epoch'), validators=[Optional(),NumberRange(min=46066.0)])
    phase_period = FloatField(_LABELS.get('phase_period'), validators=[Optional()])
    phase_start = FloatField(_LABELS.get('phase_start'), validators=[Optional(),NumberRange(min=0, max=1)])
    phase_start_margin = FloatField(_LABELS.get('phase_start_margin'), validators=[Optional(),NumberRange(min=0, max=0.5)])
    phase_end = FloatField(_LABELS.get('phase_end'), validators=[Optional(),NumberRange(min=0, max=1)])
    phase_end_margin = FloatField(_LABELS.get('phase_end_margin'), validators=[Optional(),NumberRange(min=0, max=0.5)])
    split_interval = FloatField(_LABELS.get('split_interval'), validators=[Optional()])
    #
    # --- Other (Group)
    #
    monitor_flag = SelectField(_LABELS.get('monitor_flag'), choices=_CHOICE_NY)
    pre_id = IntegerField(_LABELS.get('pre_id'), validators=[Optional()])
    pre_min_lead = FloatField(_LABELS.get('pre_min_lead'), validators=[Optional(),NumberRange(min=0)])
    pre_max_lead = FloatField(_LABELS.get('pre_max_lead'), validators=[Optional(),NumberRange(min=0.01)])
    #
    # --- Other (Joint)
    #
    multitelescope = SelectField(_LABELS.get('multitelescope'), choices=_CHOICE_NPY)
    observatories = StringField(_LABELS.get('observatories'), validators=[Optional()])
    multitelescope_interval = FloatField(_LABELS.get('multitelescope_interval'), validators=[Optional()])
    #
    # --- HRC
    #
    hrc_timing_mode = SelectField(_LABELS.get('hrc_timing_mode'), choices=_CHOICE_NNY)
    hrc_zero_block = SelectField(_LABELS.get('hrc_zero_block'), choices=_CHOICE_NNY)
    hrc_si_mode = StringField(_LABELS.get('hrc_si_mode'), validators=[Optional()])
    #
    # --- ACIS (Chips)
    #
    exp_mode = SelectField(_LABELS.get('exp_mode'), choices=((None,"NA"),("TE","TE"),("CC","CC")))
    bep_pack = SelectField(_LABELS.get('bep_pack'), choices = _CHOICE_EVENT)
    frame_time = FloatField(_LABELS.get('frame_time'), validators=[Optional(),NumberRange(min=0, max=10)])
    most_efficient = SelectField(_LABELS.get('most_efficient'), choices = _CHOICE_NNY)
    ccdi0_on = SelectField(_LABELS.get('ccdi0_on'), choices=_CHOICE_CHIP)
    ccdi1_on = SelectField(_LABELS.get('ccdi1_on'), choices=_CHOICE_CHIP)
    ccdi2_on = SelectField(_LABELS.get('ccdi2_on'), choices=_CHOICE_CHIP)
    ccdi3_on = SelectField(_LABELS.get('ccdi3_on'), choices=_CHOICE_CHIP)
    ccds0_on = SelectField(_LABELS.get('ccds0_on'), choices=_CHOICE_CHIP)
    ccds1_on = SelectField(_LABELS.get('ccds1_on'), choices=_CHOICE_CHIP)
    ccds2_on = SelectField(_LABELS.get('ccds2_on'), choices=_CHOICE_CHIP)
    ccds3_on = SelectField(_LABELS.get('ccds3_on'), choices=_CHOICE_CHIP)
    ccds4_on = SelectField(_LABELS.get('ccds4_on'), choices=_CHOICE_CHIP)
    ccds5_on = SelectField(_LABELS.get('ccds5_on'), choices=_CHOICE_CHIP)
    #
    # --- ACIS (Subarray)
    #
    subarray = SelectField(_LABELS.get('subarray'), choices=_CHOICE_SUBARRAY)
    subarray_start_row = IntegerField(_LABELS.get('subarray_start_row'), validators=[Optional(),NumberRange(min=1, max=925)])
    subarray_row_count = IntegerField(_LABELS.get('subarray_row_count'), validators=[Optional(),NumberRange(min=101, max=1024)])
    duty_cycle = SelectField(_LABELS.get('duty_cycle'), choices=_CHOICE_NNY)
    secondary_exp_count = FloatField(_LABELS.get('secondary_exp_count'), validators=[Optional(),NumberRange(min=0, max=15)])
    primary_exp_time = FloatField(_LABELS.get('primary_exp_time'), validators=[Optional(),NumberRange(min=0, max=10)])
    onchip_sum = SelectField(_LABELS.get('onchip_sum'), choices=_CHOICE_NNY)
    onchip_row_count = IntegerField(_LABELS.get('onchip_row_count'), validators=[Optional(),NumberRange(min=1, max=512)])
    onchip_column_count = IntegerField(_LABELS.get('onchip_column_count'), validators=[Optional(),NumberRange(min=1, max=512)])
    eventfilter = SelectField(_LABELS.get('eventfilter'), choices=_CHOICE_NNY)
    eventfilter_lower = FloatField(_LABELS.get('eventfilter_lower'), validators=[Optional(),NumberRange(min=0, max=15)])
    eventfilter_higher = FloatField(_LABELS.get('eventfilter_higher'), validators=[Optional(),NumberRange(min=0, max=15)])
    multiple_spectral_lines = SelectField(_LABELS.get('multiple_spectral_lines'), choices=_CHOICE_NNY)
    spectra_max_count = FloatField(_LABELS.get('spectra_max_count'), validators=[Optional(),NumberRange(min=1, max=100000)])
    #
    # --- ACIS Window
    #
    spwindow_flag = SelectField(_LABELS.get('spwindow_flag'), choices=_CHOICE_NY)
    window_ranks = FieldList(FormField(WindowRank, label=_LABELS.get('window_ranks')))
    #
    # --- Submission
    #
    submit_choice = RadioField(_LABELS.get('submit_choice'), choices=_CHOICE_SUBMIT, default='norm', validators=[Optional()])
    multiobsid = StringField(_LABELS.get('multiobsid'), validators=[Optional()])
    submit = SubmitField(_LABELS.get('submit'))
    refresh = SubmitField("Refresh")
    #
    # --- Templates for generating new ranks. Ignore all form data from these.
    # --- Hidden behind div which never appears to the user.
    #
    template_time = FormField(TimeRank)
    template_roll = FormField(RollRank)
    template_window = FormField(WindowRank)

class ConfirmForm(FlaskForm):
    """
    Extension of FlaskForm for the parameter change confirmation page.
    """
    previous_page = SubmitField(_LABELS.get('previous_page'))
    finalize = SubmitField(_LABELS.get('finalize'))

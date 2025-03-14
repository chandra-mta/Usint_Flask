"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, FormField, FieldList, IntegerField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Length
from datetime import datetime


#
#---- Common Choice of Pulldown Fields
#
_CHOICE_NNPY = ((None, 'NA'), ('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'),)
_CHOICE_NY   = (('N','NO'), ('Y','YES'),)
_CHOICE_NNY  = ((None, 'NA'), ('N', 'NO'), ('Y', 'YES'),)
_CHOICE_CP   = (('Y','CONSTRAINT'),('P','PREFERENCE'),)
_CHOICE_NNPC = ((None,'NA'),('N','NO'), ('P','PREFERENCE'), ('Y', 'CONSTRAINT'),)

_USINT_DATETIME_FORMAT = "%b-%d-%Y %H:%M"

"""
**CONCEPT MEMO**: All of the variable and function names within the form classes follow specific FlaskForm criteria in order to
allow for Jinja Template page generation to input initial data into the Ocat Form using the data argument, as well as validate
input selections for fields with the validate_<field name> functions. Changing these names will break the form validation unless matched with corresponding
initial data dictionary keys and field names.
"""


class GeneralParamForm(FlaskForm):
    targname = StringField("Target Name")

    choice = ("ACIS-I", "ACIS-S", "HRC-I", "HRC-S")
    instrument = SelectField("Instrument :", choices=[(x, x) for x in choice])

    choice = (None, "LETG", "HETG")
    grating = SelectField("Grating :", choices=[(x, x) for x in choice])

    choice = ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')
    type = SelectField("Type :", choices=[(x, x) for x in choice])

    ra_hms = StringField("RA (HMS) :")
    dec_dms = StringField("DEC (DMS) :")

    y_det_offset = StringField("Offset Y :")
    z_det_offset = StringField("Offset Z :")
    trans_offset = StringField("Z-Sim :")
    focus_offset = StringField("Sim-Focus :")

    uninterrupt = SelectField("Uninterrupted Obs :", choices=_CHOICE_NNPY)
    extended_src = SelectField("Extended SRC :", choices=_CHOICE_NY)
    obj_flag = SelectField("Solar System Object :", choices=[(x, x) for x in ('NO', 'MT', 'SS')])
    object = SelectField("Object :", choices=[(x, x) for x in (None, 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')])
    photometry_flag = SelectField("Photometry :", choices=_CHOICE_NNY)
    vmagnitude = StringField("V Mag :")
    est_cnt_rate = StringField("Count Rate :")
    forder_cnt_rate = StringField("1st Order Rate :")

class DitherParamForm(FlaskForm):
    dither_flag  = SelectField("Dither :",  choices=_CHOICE_NNY,)

class TimeParamForm(FlaskForm):
    time_ordr = IntegerField("Rank")
    window_constraint = FieldList(SelectField("Window Constraint",choices=_CHOICE_NNPC))
    tstart = FieldList(DateTimeField("Start", format=_USINT_DATETIME_FORMAT, validators=[DataRequired()]))
    tstop = FieldList(DateTimeField("Stop", format=_USINT_DATETIME_FORMAT, validators=[DataRequired()]))
    
    all_invalid_time = []
    #: TODO Why are both validations triggering when only one datetime box is erroring?
    #: Now always triggering when submitting... try approach with custom validator class instead to feed into the Datetime Field.
    def validate_tstart(form,field_list):
        for field in field_list:
            try:
                datetime.strptime(field.data, _USINT_DATETIME_FORMAT)
            except (ValueError, TypeError):
                error = ValidationError(f'Invalid datetime format in {field.label.text}. Use MMM-DD-YYY HH:MM')
                form.all_invalid_time.append(error)
                raise error
            
    def validate_tstop(form,field_list):
        for field in field_list:
            try:
                datetime.strptime(field.data, _USINT_DATETIME_FORMAT)
            except (ValueError, TypeError):
                error = ValidationError(f'Invalid datetime format in {field.label.text}. Use MMM-DD-YYY HH:MM')
                form.all_invalid_time.append(error)
                raise error

class SubmitParamForm(FlaskForm):
    refresh = SubmitField("Refresh :")
    open_dither = SubmitField("Open Dither :")
    open_time = SubmitField("Open Time Constraints :")
    open_roll = SubmitField("Open Roll Constraints :")
    open_awin = SubmitField("Open Window Constraints :")
    submit = SubmitField("Submit")

class OcatParamForm(FlaskForm):
    """
    Extension of FlaskForm for Ocat Parameter Data Page Form.
    Includes all parameters with corresponding editable fields.
    Note that this means non-editable information is rendered directly by flask template and not by form method.
    """
    gen_param = FormField(GeneralParamForm)
    dither_param = FormField(DitherParamForm)
    time_param = FormField(TimeParamForm)
    submit = FormField(SubmitParamForm)
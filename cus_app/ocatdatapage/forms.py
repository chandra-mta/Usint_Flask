"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, FormField, FieldList, HiddenField
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
_MONTH_LIST = month_abbr[1:]
_MONTH_CHOICE = [(None,'NA')] + [(x,x) for x in _MONTH_LIST]
_DAY_LIST = [f"{x:02}" for x in range(1,32)]
_DAY_CHOICE = [(None,'NA')] + [(x,x) for x in _DAY_LIST]

_USINT_DATETIME_FORMAT = "%b-%d-%Y %H:%M"

"""
**CONCEPT MEMO**: All of the variable and function names within the form classes follow specific FlaskForm criteria in order to
allow for Jinja Template page generation to input initial data into the Ocat Form using the data argument, as well as validate
input selections for fields with the validate_<field name> functions. Changing these names will break the form validation unless matched with corresponding
initial data dictionary keys and field names.
"""

class GeneralParamForm(FlaskForm):
    targname = StringField("Target Name", validators=[DataRequired()])

    choice = ("ACIS-I", "ACIS-S", "HRC-I", "HRC-S")
    instrument = SelectField("Instrument", choices=[(x, x) for x in choice])

    choice = (None, "LETG", "HETG")
    grating = SelectField("Grating", choices=[(x, x) for x in choice])

    choice = ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')
    type = SelectField("Type", choices=[(x, x) for x in choice])

    ra_hms = StringField("RA (HMS)")
    dec_dms = StringField("DEC (DMS)")

    y_det_offset = StringField("Offset Y")
    z_det_offset = StringField("Offset Z")
    trans_offset = StringField("Z-Sim")
    focus_offset = StringField("Sim-Focus")

    uninterrupt = SelectField("Uninterrupted Obs", choices=_CHOICE_NNPY)
    extended_src = SelectField("Extended SRC", choices=_CHOICE_NY)
    obj_flag = SelectField("Solar System Object", choices=[(x, x) for x in ('NO', 'MT', 'SS')])
    object = SelectField("Object", choices=[(x, x) for x in (None, 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')])
    photometry_flag = SelectField("Photometry", choices=_CHOICE_NNY)
    vmagnitude = StringField("V Mag")
    est_cnt_rate = StringField("Count Rate")
    forder_cnt_rate = StringField("1st Order Rate")

class DitherParamForm(FlaskForm):
    dither_flag  = SelectField("Dither",  choices=_CHOICE_NNY,)

class TimeParamForm(FlaskForm):
    time_ordr = HiddenField("Rank") #: Hidden as this can change in the form but indirectly.
    window_constraint = FieldList(SelectField("Window Constraint",choices=_CHOICE_NNPC)) #: label fix?

    tstart_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")
    tstop_year = FieldList(SelectField("Year", choices=_YEAR_CHOICE), label="Year")

    tstart_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")
    tstop_month = FieldList(SelectField("Month", choices=_MONTH_CHOICE), label="Month")

    tstart_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Day")
    tstop_date = FieldList(SelectField("Day", choices=_DAY_CHOICE), label="Year")
    #: TODO include validators for time
    tstart_time = FieldList(StringField("Time"),label="Time (24hr)")
    tstop_time = FieldList(StringField("Time"),label="Time (24hr)")
    

class SubmitParamForm(FlaskForm):
    refresh = SubmitField("Refresh")
    open_dither = SubmitField("Open Dither")
    open_time = SubmitField("Open Time Constraints")
    open_roll = SubmitField("Open Roll Constraints")
    open_awin = SubmitField("Open Window Constraints")
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
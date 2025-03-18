"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 20.025

"""
from flask import request
from flask_wtf import FlaskForm
from wtforms import Field, SelectField, StringField, SubmitField, FormField, FloatField, FieldList, HiddenField
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

class PlainTextField(Field):
    def __call__(self, **kwargs):
        return str(self.data) if self.data is not None else ''

    def _value(self):
        return str(self.data) if self.data is not None else ''
"""
class DitherParamForm(FlaskForm):
    dither_flag = SelectField("Dither",  choices=_CHOICE_NNY)
    
    y_amp_asec = StringField("Y_Amp (in arcsec)", default = 0.0)
    y_freq_asec = StringField("Y_Freq (in arcsec/sec)", default = 0.0)
    y_phase = StringField("Y_Phase", default = 0.0)
    
    y_amp = StringField("Y_Amp (in degrees)", default = 0.0)
    y_freq = StringField("Y_Freq (in degrees/sec)", default = 0.0)

    z_amp_asec = StringField("Z_Amp (in arcsec)", default = 0.0)
    z_freq_asec = StringField("Z_Freq (in arcsec/sec)", default = 0.0)
    z_phase = StringField("Z_Phase", default = 0.0)
    
    z_amp = StringField("Z_Amp (in degrees)", default = 0.0)
    z_freq = StringField("Z_Freq (in degrees/sec)", default = 0.0)
"""

class DitherParamForm(FlaskForm):
    dither_flag = SelectField("Dither",  choices=_CHOICE_NNY)
    
    y_amp_asec = FloatField("Y_Amp (in arcsec)", default = 0.0)
    y_freq_asec = FloatField("Y_Freq (in arcsec/sec)", default = 0.0)
    y_phase = FloatField("Y_Phase", default = 0.0)
    
    y_amp = FloatField("Y_Amp (in degrees)", default = 0.0)
    y_freq = FloatField("Y_Freq (in degrees/sec)", default = 0.0)

    z_amp_asec = FloatField("Z_Amp (in arcsec)", default = 0.0)
    z_freq_asec = FloatField("Z_Freq (in arcsec/sec)", default = 0.0)
    z_phase = FloatField("Z_Phase", default = 0.0)
    
    z_amp = FloatField("Z_Amp (in degrees)", default = 0.0)
    z_freq = FloatField("Z_Freq (in degrees/sec)", default = 0.0)

class OcatParamForm(FlaskForm):
    """
    Extension of FlaskForm for Ocat Parameter Data Page Form.
    Includes all parameters with corresponding editable fields.
    Note that this means non-editable information is rendered directly by flask template and not by form method.
    """
    dither_param = FormField(DitherParamForm)
    
    open_dither = SubmitField("Open Dither")
    refresh = SubmitField("Refresh")
    submit = SubmitField("Submit")
"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""

from re import S
from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Length


#
#---- Common Choice of Pulldown Fields
#
_CHOICE_NNPY = ((None, 'NA'), ('N', 'NO'), ('P','PREFERENCE'), ('Y','YES'),)
_CHOICE_NY   = (('N','NO'), ('Y','YES'),)
_CHOICE_NNY  = ((None, 'NA'), ('N', 'NO'), ('Y', 'YES'),)
_CHOICE_CP   = (('Y','CONSTRAINT'),('P','PREFERENCE'),)
_CHOICE_NNPC = ((None,'NA'),('N','NO'), ('P','PREFERENCE'), ('Y', 'CONSTRAINT'),)

class GeneralParamForm(FlaskForm):
    targname = StringField("Target Name")

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

    #
    #--- Dither
    #
    dither_param = FormField(DitherParamForm)
    
    submit = FormField(SubmitParamForm)
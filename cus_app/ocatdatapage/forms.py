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
    seq_nbr = IntegerField("Sequence Number", render_kw={'readonly': True})
    status = StringField("Status", render_kw={'readonly': True})
    obsid = IntegerField("Obsid", render_kw={'readonly': True})
    proposal_number = IntegerField("Proposal Number", render_kw={'readonly': True})
    proposal_title = StringField("Proposal Title", render_kw={'readonly': True})
    obs_ao_str = StringField("Obs AO Status", render_kw={'readonly': True})

    targname = StringField("Target Name", validators=[DataRequired()])
    si_mode = StringField("SI Mode", render_kw={'readonly': True})
    aca_mode = StringField("ACA Mode", render_kw={'readonly': True})

    choice = ("ACIS-I", "ACIS-S", "HRC-I", "HRC-S")
    instrument = SelectField("Instrument", choices=[(x, x) for x in choice])
    choice = (None, "LETG", "HETG")
    grating = SelectField("Grating", choices=[(x, x) for x in choice])
    choice = ('GO', 'TOO', 'GTO', 'CAL', 'DDT', 'CAL_ER', 'ARCHIVE', 'CDFS', 'CLP')
    obs_type = SelectField("Type", choices=[(x, x) for x in choice])

    pi_name = StringField("PI Name", render_kw={'readonly': True})
    observer = StringField("Observer", render_kw={'readonly': True})
    approved_exposure_time = StringField("Approved Exposure Time", render_kw={'readonly': True})
    rem_exp_time = StringField("Remaining Exposure Time", render_kw={'readonly': True})

    proposal_joint = StringField("Joint", render_kw={'readonly': True})
    proposal_hst = StringField("HST Approved Time", render_kw={'readonly': True})
    proposal_noao = StringField("NOAO Approved Time", render_kw={'readonly': True})
    proposal_xmm = StringField("XMM Approved Time", render_kw={'readonly': True})
    proposal_rxte = StringField("RXTE Approved Time", render_kw={'readonly': True})
    proposal_vla = StringField("VLA Approved Time", render_kw={'readonly': True})
    proposal_vlba = StringField("VLBA Approved Time", render_kw={'readonly': True})

    soe_st_sched_date = StringField("Scheduled Date", render_kw={'readonly': True})
    lts_lt_plan = StringField("LST Date", render_kw={'readonly': True})

    rass = StringField("RASS", render_kw={'readonly': True})
    rosat = StringField("ROSAT", render_kw={'readonly': True})
    dss = StringField("DSS", render_kw={'readonly': True})

    ra_hms = StringField("RA (HMS)", default='00:00:00.0000')
    dec_dms = StringField("Dec (DMS)", default='+00:00:00.0000')
    planned_roll = StringField("Planned Roll", render_kw={'readonly': True})
    ra = FloatField("RA",default = 0.0, render_kw={'readonly': True})
    dec = FloatField("Dec",default = 0.0, render_kw={'readonly': True})
    soe_roll = StringField("Roll Observed", render_kw={'readonly': True})

    y_det_offset = StringField("Offset Y")
    z_det_offset = StringField("Offset Z")
    trans_offset = StringField("Z-Sim")
    focus_offset = StringField("Sim-Focus")
    raster_scan = StringField("Raster Scan", render_kw={'readonly': True})

    uninterrupt = SelectField("Uninterrupted Obs", choices=_CHOICE_NNPY)
    extended_src = SelectField("Extended SRC", choices=_CHOICE_NY)
    obj_flag = SelectField("Solar System Object", choices=[(x, x) for x in ('NO', 'MT', 'SS')])
    object = SelectField("Object", choices=[(x, x) for x in (None, 'NEW','ASTEROID', 'COMET', 'EARTH', 'JUPITER', 'MARS','MOON', 'NEPTUNE', 'PLUTO', 'SATURN', 'URANUS', 'VENUS')])
    photometry_flag = SelectField("Photometry", choices=_CHOICE_NNY)
    vmagnitude = StringField("V Mag")
    est_cnt_rate = StringField("Count Rate")
    forder_cnt_rate = StringField("1st Order Rate")

"""
class DitherParamForm(FlaskForm):
    dither_flag = SelectField("Dither",  choices=_CHOICE_NNY)
    
    y_amp_asec = StringField("Y_Amp (in arcsec)", default = 0.0)
    y_freq_asec = StringField("Y_Freq (in arcsec/sec)", default = 0.0)
    y_phase = StringField("Y_Phase", default = 0.0)
    
    y_amp = StringField("Y_Amp (in degrees)", default = 0.0, render_kw={'readonly': True})
    y_freq = StringField("Y_Freq (in degrees/sec)", default = 0.0, render_kw={'readonly': True})

    z_amp_asec = StringField("Z_Amp (in arcsec)", default = 0.0)
    z_freq_asec = StringField("Z_Freq (in arcsec/sec)", default = 0.0)
    z_phase = StringField("Z_Phase", default = 0.0)
    
    z_amp = StringField("Z_Amp (in degrees)", default = 0.0, render_kw={'readonly': True})
    z_freq = StringField("Z_Freq (in degrees/sec)", default = 0.0, render_kw={'readonly': True})
"""

class DitherParamForm(FlaskForm):
    dither_flag = SelectField("Dither",  choices=_CHOICE_NNY)
    
    y_amp_asec = FloatField("Y_Amp (in arcsec)", default = 0.0)
    y_freq_asec = FloatField("Y_Freq (in arcsec/sec)", default = 0.0)
    y_phase = FloatField("Y_Phase", default = 0.0)
    
    y_amp = FloatField("Y_Amp (in degrees)", default = 0.0, render_kw={'readonly': True})
    y_freq = FloatField("Y_Freq (in degrees/sec)", default = 0.0, render_kw={'readonly': True})

    z_amp_asec = FloatField("Z_Amp (in arcsec)", default = 0.0)
    z_freq_asec = FloatField("Z_Freq (in arcsec/sec)", default = 0.0)
    z_phase = FloatField("Z_Phase", default = 0.0)
    
    z_amp = FloatField("Z_Amp (in degrees)", default = 0.0, render_kw={'readonly': True})
    z_freq = FloatField("Z_Freq (in degrees/sec)", default = 0.0, render_kw={'readonly': True})

class OcatParamForm(FlaskForm):
    """
    Extension of FlaskForm for Ocat Parameter Data Page Form.
    Includes all parameters with corresponding editable fields.
    Note that this means non-editable information is rendered directly by flask template and not by form method.
    """
    gen_param = FormField(GeneralParamForm)
    dither_param = FormField(DitherParamForm)
    
    open_dither = SubmitField("Open Dither")
    refresh = SubmitField("Refresh")
    submit = SubmitField("Submit")
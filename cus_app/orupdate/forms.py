"""
**orupdate/forms.py**: Flask WTForm of the Target Status Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 06, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, Field
from wtforms.widgets import Input
from datetime import datetime
import json
import os

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

class SignoffRow(FlaskForm):
    gen = SubmitField("Signoff")
    acis = SubmitField("Signoff")
    acis_si = SubmitField("Signoff")
    hrc_si = SubmitField("Signoff")
    usint = SubmitField("Signoff")
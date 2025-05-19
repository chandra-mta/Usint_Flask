"""
**scheduler/forms.py**: Flask WTForm of the TOO Scheduler Page.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 19, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField

class ScheduleRow(FlaskForm):
    unlock = SubmitField("Unlock")
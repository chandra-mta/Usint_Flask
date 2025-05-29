"""
**rm_submission/forms.py**: Flask WTForm of the Remove Submission Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 015, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField

class RemoveRow(FlaskForm):
    """
    Form for selecting signoff column for removal.
    """
    revision = SubmitField("Remove")
    general = SubmitField("Remove")
    acis = SubmitField("Remove")
    acis_si = SubmitField("Remove")
    hrc_si = SubmitField("Remove")
    usint = SubmitField("Remove")
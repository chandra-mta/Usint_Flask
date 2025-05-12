"""
**express/forms.py**: Flask WTForm of the Express Approval Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 12, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField

class ExpressApprovalForm(FlaskForm):
    multiobsid = StringField()
    submit = SubmitField("Submit")
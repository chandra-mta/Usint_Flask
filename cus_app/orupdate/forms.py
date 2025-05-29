"""
**orupdate/forms.py**: Flask WTForm of the Target Status Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 06, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import Optional

class SignoffRow(FlaskForm):
    """
    Signoff Row Buttons Form
    """
    gen = SubmitField("Signoff")
    acis = SubmitField("Signoff")
    acis_si = SubmitField("Signoff")
    hrc_si = SubmitField("Signoff")
    usint = SubmitField("Signoff")
    approve = SubmitField("Signoff & Approve")

class OrderForm(FlaskForm):
    """
    Form for selecting the display order of the revisions
    """
    order_submission = SubmitField("Date of Submission")
    order_obsid = SubmitField("Obsid")
    order_username = SubmitField("Username:")
    username = StringField(validators=[Optional()])
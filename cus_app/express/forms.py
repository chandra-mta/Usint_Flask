"""
**express/forms.py**: Flask WTForm of the Express Approval Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 12, 2025

"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField

class ExpressApprovalForm(FlaskForm):
    """
    Form for inputting list of obsids for express approval.
    """
    multiobsid = StringField()
    submit = SubmitField("Submit")

class ConfirmForm(FlaskForm):
    """
    Extension of FlaskForm to confirm change.
    """
    previous_page = SubmitField("Previous Page")
    finalize = SubmitField("Finalize")

"""
**ocatdatapage/forms.py**: Flask WTForm of the Ocat Data Page

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 13, 2025

"""
from flask              import request
from flask_wtf          import FlaskForm
from wtforms            import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length

class OcatParamForm(FlaskForm):

    obsid = StringField('Obsid')
    targname = StringField('Target Name')
    submit = SubmitField('Submit')
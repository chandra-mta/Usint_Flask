from flask_wtf          import FlaskForm
from wtforms            import StringField, SubmitField
from wtforms.validators import DataRequired

class ObsidRevForm(FlaskForm):
    """
    Form for inputting an obsid.rev for parameter display
    """
    obsidrev    = StringField('Obsidrev', validators=[DataRequired()])
    submit      = SubmitField('Submit')
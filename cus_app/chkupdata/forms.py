from flask_wtf          import FlaskForm
from wtforms            import StringField, SubmitField
from wtforms.validators import DataRequired

class ObsidRevForm(FlaskForm):
    obsidrev    = StringField('Obsidrev', validators=[DataRequired()])
    submit      = SubmitField('Submit')
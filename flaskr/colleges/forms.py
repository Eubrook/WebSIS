import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, IntegerField
from wtforms.validators import DataRequired

class AddCollegeForm(FlaskForm):
    college_code = StringField('College Code', validators=[DataRequired()])
    college_name = StringField('College Name', validators=[DataRequired()])
    submit = SubmitField ('Add College')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, ValidationError
from wtforms.validators import DataRequired
from .models import college_exists  # Import the model function instead of using mysql directly

class AddCollegeForm(FlaskForm):
    college_code = StringField('College Code', validators=[DataRequired()])
    college_name = StringField('College Name', validators=[DataRequired()])
    submit = SubmitField('Add College')

    def validate_college_code(self, field):
        if college_exists(field.data):
            raise ValidationError("College code already exists.")

class UpdateCollegeForm(FlaskForm):
    college_code = StringField('College Code', validators=[DataRequired()])
    college_name = StringField('College Name', validators=[DataRequired()])
    original_college_code = HiddenField()
    submit = SubmitField('Update College')

    def validate_college_code(self, field):
        # Allow same value as original but not if already used by another
        if field.data != self.original_college_code.data and college_exists(field.data):
            raise ValidationError("College code already exists.")

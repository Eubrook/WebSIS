from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectField, HiddenField
from wtforms.validators import DataRequired

from .models import college_exists, is_course_code_duplicate, is_course_name_duplicate

class AddCourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    college_code = SelectField('College Code', validators=[DataRequired()])
    submit = SubmitField('Add Course')

    def validate_college_code(self, field):
        if not college_exists(field.data):
            raise ValidationError("College code does not exist. Please add it first.")

    def validate_course_code(self, field):
        if is_course_code_duplicate(field.data):
            raise ValidationError("This course code already exists.")

    def validate_course_name(self, field):
        if is_course_name_duplicate(field.data):
            raise ValidationError("This course name already exists.")


class UpdateCourseForm(FlaskForm):
    original_course_code = HiddenField('Original Course Code')
    course_code = StringField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    college_code = SelectField('College Code', validators=[DataRequired()])
    submit = SubmitField('Update Course')

    def validate_college_code(self, field):
        if not college_exists(field.data):
            raise ValidationError("College code does not exist. Please add it first.")

    def validate_course_code(self, field):
        # Skip duplicate check if course_code is unchanged
        if field.data != self.original_course_code.data:
            if is_course_code_duplicate(field.data):
                raise ValidationError("This course code already exists.")

    def validate_course_name(self, field):
        # Allow unchanged name or check for duplicates
        if is_course_name_duplicate(field.data, exclude_code=self.original_course_code.data):
            raise ValidationError("This course name already exists.")

import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, IntegerField, SelectField, FileField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime
from .models import student_id_exists, course_code_exists  # import your helpers

# File size validator (standalone)
def file_size_limit(max_size_mb):
    max_bytes = max_size_mb * 1024 * 1024
    def _file_size_limit(form, field):
        if field.data:
            # field.data is a Werkzeug FileStorage object
            file = field.data
            file.seek(0, 2)  # Seek to end of file
            size = file.tell()
            file.seek(0)     # Reset pointer to start for later reading
            if size > max_bytes:
                raise ValidationError(f'File size must be less than {max_size_mb} MB.')
    return _file_size_limit

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

class AddStudentForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")
    ])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture', validators=[
    file_size_limit(2),
    FileAllowed(ALLOWED_EXTENSIONS, 'Only image files with extensions jpg, jpeg, png are allowed.')
    ])
    submit = SubmitField('Add Student')

    def validate_id(self, field):
        # Check format
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")

        # Check year
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")

        # Check uniqueness
        if student_id_exists(field.data):
            raise ValidationError("This student ID already exists. Please use a unique ID.")

    def validate_course_code(self, field):
        if not course_code_exists(field.data):
            raise ValidationError("Course code does not exist. Please add it first.")



class UpdateStudentForm(FlaskForm):
    original_id = HiddenField('Original ID')
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture', validators=[
    file_size_limit(2),
    FileAllowed(ALLOWED_EXTENSIONS, 'Only image files with extensions jpg, jpeg, png are allowed.')
    ])
    submit = SubmitField('Update Student')

    def validate_id(self, field):
        # Check format
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")

        # Check year is not in the future
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")

        # Check if ID was changed and if the new one already exists
        if field.data != self.original_id.data and student_id_exists(field.data):
            raise ValidationError("A student with this ID already exists.")

    def validate_course_code(self, field):
        if not course_code_exists(field.data):
            raise ValidationError("Course code does not exist. Please add it first.")
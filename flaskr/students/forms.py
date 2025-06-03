import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError, IntegerField, HiddenField, FileField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
from flaskr import mysql

# Define file size validator outside the classes for reuse
def file_size_limit(max_size_mb):
    max_bytes = max_size_mb * 1024 * 1024
    def _file_size_limit(form, field):
        if field.data:
            field.data.stream.seek(0, 2)  # seek to end of file
            file_size = field.data.stream.tell()
            field.data.stream.seek(0)     # reset pointer
            if file_size > max_bytes:
                raise ValidationError(f'File size must be less than {max_size_mb} MB.')
    return _file_size_limit

class AddStudentForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture', validators=[file_size_limit(2)])  # 2 MB limit
    submit = SubmitField('Add Student')

    def validate_id(self, field):
        # 1. Validate pattern
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")

        # 2. Validate year
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")

        # 3. Check uniqueness in the database using MySQL
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            raise ValidationError("This student ID already exists. Please use a unique ID.")

    def validate_course_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()
        if result[0] == 0:
            raise ValidationError("Course code does not exist. Please add it first.")


    def file_size_limit(max_size_mb):
        max_bytes = max_size_mb * 1024 * 1024
        def _file_size_limit(form, field):
            if field.data:
                field.data.stream.seek(0, 2)  # seek to end of file
                file_size = field.data.stream.tell()
                field.data.stream.seek(0)     # reset pointer
                if file_size > max_bytes:
                    raise ValidationError(f'File size must be less than {max_size_mb} MB.')
        return _file_size_limit


class UpdateStudentForm(FlaskForm):
    original_id = HiddenField('Original ID')
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture', validators=[file_size_limit(2)])  # 2 MB limit
    submit = SubmitField('Update Student')

    def validate_id(self, field):
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")
        
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")
        
        # Only check duplicates if ID changed
        if field.data != self.original_id.data:
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (field.data,))
            result = cur.fetchone()
            cur.close()
            if result[0] > 0:
                raise ValidationError("A student with this ID already exists.")


            # Only check for duplicates if ID was changed
            if field.data != self.original_id.data:
                cur = mysql.connection.cursor()
                cur.execute("SELECT COUNT(*) FROM students WHERE id = %s", (field.data,))
                result = cur.fetchone()
                cur.close()
                if result[0] > 0:
                    raise ValidationError("A student with this ID already exists.")

    def validate_course_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()
        if result[0] == 0:
            raise ValidationError("Course code does not exist. Please add it first.")

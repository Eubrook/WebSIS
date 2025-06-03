import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError, IntegerField, HiddenField, FileField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
from flaskr import mysql

class AddStudentForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture')
    submit = SubmitField('Add Student')

    # This attribute will be set dynamically if duplicate name found
    name_duplicate_warning = False

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

    def validate_first_name(self, field):
        last_name = self.last_name.data

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM students 
            WHERE first_name = %s AND last_name = %s
        """, (field.data, last_name))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            # Set flag instead of raising error, to handle warning in your view/template
            self.name_duplicate_warning = True


class UpdateStudentForm(FlaskForm):
    original_id = HiddenField('Original ID')
    id = StringField('ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    year_level = IntegerField('Year Level', validators=[
        DataRequired(), NumberRange(min=1, max=10, message="Year level must be between 1 and 10")])
    course_code = StringField('Course Code', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    prof_pic = FileField('Profile Picture')
    submit = SubmitField('Update Student')

    name_duplicate_warning = False

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

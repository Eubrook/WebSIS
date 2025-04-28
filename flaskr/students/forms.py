
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError, IntegerField, HiddenField
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
    submit = SubmitField('Add Student')

    def validate_id(form, field):
        pattern = r'^\d{4}-\d{4}$'  #allowed pattern for id
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")
        
    def validate_course_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] == 0:
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
    submit = SubmitField('Update Student')

    def validate_id(form, field):
        pattern = r'^\d{4}-\d{4}$'  #allowed pattern for id
        if not re.match(pattern, field.data):
            raise ValidationError("ID must be in the format YYYY-NNNN (e.g., 2023-1234)")
        year = int(field.data.split('-')[0])
        if year > datetime.now().year:
            raise ValidationError("Year in ID cannot be in the future.")
        
    def validate_course_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] == 0:
            raise ValidationError("Course code does not exist. Please add it first.")

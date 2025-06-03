from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectField, HiddenField
from wtforms.validators import DataRequired
from flaskr import mysql

class AddCourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    college_code = SelectField('College Code', validators=[DataRequired()])
    submit = SubmitField('Add Course')

    def validate_college_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] == 0:
            raise ValidationError("College code does not exist. Please add it first.")

    def validate_course_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            raise ValidationError("This course code already exists.")

    def validate_course_name(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_name = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            raise ValidationError("This course name already exists.")


class UpdateCourseForm(FlaskForm):
    original_course_code = HiddenField('Original Course Code')
    course_code = StringField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    college_code = SelectField('College Code', validators=[DataRequired()])
    submit = SubmitField('Update Course')

    def validate_college_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] == 0:
            raise ValidationError("College code does not exist. Please add it first.")

    def validate_course_code(self, field):
        # Skip duplicate check if course_code is unchanged
        if field.data == self.original_course_code.data:
            return

        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            raise ValidationError("This course code already exists.")

    def validate_course_name(self, field):
        # For update, make sure we exclude the current course name if unchanged
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM courses 
            WHERE course_name = %s AND course_code != %s
        """, (field.data, self.original_course_code.data))
        result = cur.fetchone()
        cur.close()

        if result[0] > 0:
            raise ValidationError("This course name already exists.")

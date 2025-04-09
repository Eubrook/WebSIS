
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, IntegerField
from wtforms.validators import DataRequired
from flaskr import mysql

class AddCourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    college_code = StringField('College Code', validators=[DataRequired()])
    submit = SubmitField('Add Course')

    def validate_college_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()

        if result[0] == 0:
            raise ValidationError("College code does not exist. Please add it first.")

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, ValidationError
from wtforms.validators import DataRequired
from flaskr import mysql

class AddCollegeForm(FlaskForm):
    college_code = StringField('College Code', validators=[DataRequired()])
    college_name = StringField('College Name', validators=[DataRequired()])
    submit = SubmitField('Add College')

    def validate_college_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()
        if result[0] > 0:
            raise ValidationError("College code already exists.")

class UpdateCollegeForm(FlaskForm):
    college_code = StringField('College Code', validators=[DataRequired()])
    college_name = StringField('College Name', validators=[DataRequired()])
    original_college_code = HiddenField()
    submit = SubmitField('Update College')

    def validate_college_code(self, field):
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (field.data,))
        result = cur.fetchone()
        cur.close()
        if result[0] > 0 and field.data != self.original_college_code.data:
            raise ValidationError("College code already exists.")



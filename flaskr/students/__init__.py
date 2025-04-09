from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Response, jsonify
import json
from flaskr import mysql
from flask import render_template, request, redirect, url_for, flash
from flaskr import mysql
from .forms import AddStudentForm, UpdateStudentForm # Import the form class



students_page = Blueprint('students_page', __name__)


@students_page.route('/students', methods=['GET', 'POST'])
def students():
    cur = mysql.connection.cursor()

    # Get all course codes from the database
    cur.execute("SELECT course_code FROM courses")
    course_codes = [row[0] for row in cur.fetchall()]

    # Initialize form and set choices
    # Initialize forms
    form = UpdateStudentForm()
    update_form = UpdateStudentForm()  # <-- Add this
    form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]  # 

    # Handle POST (form submission)
    if request.method == 'POST' and form.validate_on_submit():
        student_id = form.id.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        year_level = form.year_level.data
        course_code = form.course_code.data
        gender = form.gender.data

        # Insert the student
        cur.execute("""
            INSERT INTO students (id, first_name, last_name, year_level, course_code, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, first_name, last_name, year_level, course_code, gender))
        mysql.connection.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students_page.students'))

    # Handle GET (including search)
    search_query = request.args.get('search', '')
    field = request.args.get('field', 'id')

    #Protect against SQL injection in search field
    allowed_fields = ['id', 'first_name', 'last_name', 'year_level', 'course_code', 'gender']
    if field not in allowed_fields:
        field = 'id'

    if search_query:
        cur.execute(f"SELECT * FROM students WHERE {field} LIKE %s", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM students")

    students = cur.fetchall()
    cur.close()

    return render_template('students/students.html', students=students, form=form, update_form=update_form, course_codes=course_codes)



@students_page.route('/search_students', methods=['GET'])
def search_students():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'  # Convert to Boolean

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    cur = mysql.connection.cursor()

    # Exact match or partial match handling
    if exact:
        sql = f"SELECT id, first_name, last_name, year_level, course_code, gender FROM students WHERE {field} = %s"
        params = (query,)
    else:
        sql = f"SELECT id, first_name, last_name, year_level, course_code, gender FROM students WHERE {field} LIKE %s"
        params = (f"%{query}%",)

    try:
        cur.execute(sql, params)
        students_data = cur.fetchall()
        cur.close()

        students_list = [
            {
                'id': student[0],
                'first_name': student[1],
                'last_name': student[2],
                'year_level': student[3],
                'course_code': student[4],
                'gender': student[5],
            }
            for student in students_data
        ]

        return Response(json.dumps(students_list), mimetype='application/json')
    except Exception as e:
        print("Error:", e)
        return Response("Error occurred", status=500)


@students_page.route('/all_students', methods=['GET'])
def all_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, first_name, last_name, year_level, course_code, gender FROM students")
    students_data = cur.fetchall()
    cur.close()

    students_list = [
        {
            'id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'year_level': student[3],
            'course_code': student[4],
            'gender': student[5],
        }
        for student in students_data
    ]
    
    return Response(json.dumps(students_list), mimetype='application/json')


@students_page.route('/students/delete/<id>', methods=['POST'])
def delete_student(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students_page.students'))



@students_page.route('/students/update_students', methods=['GET', 'POST'])
def update_students():
    cur = mysql.connection.cursor()

    # Get all course codes
    cur.execute("SELECT course_code FROM courses")
    course_codes = [row[0] for row in cur.fetchall()]

    # Initialize forms first
    add_form = AddStudentForm()
    update_form = UpdateStudentForm()

    # Then assign choices
    add_form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]

    if update_form.validate_on_submit():
        cur.execute("""
            UPDATE students
            SET id = %s,
                first_name = %s,
                last_name = %s,
                year_level = %s,
                course_code = %s,
                gender = %s
            WHERE id = %s
        """, (
            update_form.id.data,
            update_form.first_name.data,
            update_form.last_name.data,
            update_form.year_level.data,
            update_form.course_code.data,
            update_form.gender.data,
            update_form.id.data
        ))
        mysql.connection.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students_page.students'))  # Redirect after successful POST
    else:
        flash('Error updating student.', 'error')

        # ⬇️ Fetch students so the template can render properly
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        cur.close()

    return render_template(
        'students/students.html',
        students=students,
        form=add_form,
        update_form=update_form,
        course_codes=course_codes
    )


@students_page.route('/upload_profile', methods=['POST'])
def upload_profile():
    file = request.files['profile_picture']
    
    # Optional: delete previous image here before uploading new one

    if file:
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']
        public_id = upload_result['public_id']

        # Save image_url and public_id to database
        # e.g., update students SET profile_url = image_url, cloudinary_id = public_id WHERE id = ?

        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('your_profile_view'))

    flash("No file uploaded.", "error")
    return redirect(url_for('your_profile_view'))


@students_page.route('/delete_profile_picture/<string:cloudinary_id>', methods=['POST'])
def delete_profile_picture(cloudinary_id):
    try:
        cloudinary.uploader.destroy(cloudinary_id)

        # Remove reference in database
        # e.g., update students SET profile_url = NULL, cloudinary_id = NULL WHERE id = ?

        flash("Profile picture deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting image: {str(e)}", "danger")
    
    return redirect(url_for('your_profile_view'))
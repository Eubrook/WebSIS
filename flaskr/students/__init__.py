from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify
import json
from .forms import AddStudentForm, UpdateStudentForm
import cloudinary.uploader
from . import models  
from math import ceil

students_page = Blueprint('students_page', __name__)


@students_page.route('/students', methods=['GET', 'POST'])
def students():
    course_codes = models.get_all_course_codes()

    form = AddStudentForm()
    update_form = UpdateStudentForm()
    form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]

    if request.method == 'POST' and form.validate_on_submit():
        student_id = form.id.data.strip()
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        year_level = form.year_level.data
        course_code = form.course_code.data
        gender = form.gender.data
        prof_pic_url = None

        # Handle file upload
        file = request.files.get('prof_pic')
        if file and file.filename != '':
            upload_result = cloudinary.uploader.upload(file)
            prof_pic_url = upload_result.get('secure_url')

        # Insert into students table
        cur.execute("""
            INSERT INTO students (id, first_name, last_name, year_level, course_code, gender, prof_pic)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, first_name, last_name, year_level, course_code, gender, prof_pic_url))
        mysql.connection.commit()
        cur.close()

        flash('Student added successfully!', 'success')
        return redirect(url_for('students_page.students'))

    # Handle GET or failed POST - search functionality
    search_query = request.args.get('search', '').strip()
    field = request.args.get('field', 'id')

    offset = (page - 1) * rows_per_page
    total_students = models.get_students_count(search_query, field)
    total_pages = ceil(total_students / rows_per_page) if rows_per_page else 1

    students = models.get_students(search_query, field, limit=rows_per_page, offset=offset)

    return render_template('students/students.html', students=students, form=form, update_form=update_form, course_codes=course_codes)

@students_page.route('/search_students', methods=['GET'])
def search_students():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'

    try:
        students_data = models.search_students(query, field, exact)
        students_list = [
            {
                'id': student[0],
                'first_name': student[1],
                'last_name': student[2],
                'year_level': student[3],
                'course_code': student[4],
                'gender': student[5],
                'prof_pic': student[6],
            }
            for student in students_data
        ]
        return Response(json.dumps(students_list), mimetype='application/json')
    except Exception as e:
        print("Error in search_students:", e)
        return Response("Error occurred", status=500)


@students_page.route('/all_students', methods=['GET'])
def all_students():
    students_data = models.get_students()
    students_list = [
        {
            'id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'year_level': student[3],
            'course_code': student[4],
            'gender': student[5],
            'prof_pic': student[6]
        }
        for student in students_data
    ]
    return Response(json.dumps(students_list), mimetype='application/json')


@students_page.route('/students/delete/<id>', methods=['POST'])
def delete_student(id):
    models.delete_student(id)
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students_page.students'))


@students_page.route('/students/update_students', methods=['GET', 'POST'])
def update_students():
    course_codes = models.get_all_course_codes()

    add_form = AddStudentForm()
    update_form = UpdateStudentForm()
    add_form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]

    if update_form.validate_on_submit():
        original_id = request.form.get("original_id", "").strip()
        new_id = update_form.id.data.strip()

        file = request.files.get('prof_pic')
        prof_pic = None
        if file and file.filename != '':
            import cloudinary.uploader
            upload_result = cloudinary.uploader.upload(file)
            prof_pic = str(upload_result.get('secure_url'))  # <-- here too

        else:
            # No new file uploaded, keep existing profile picture
            cur.execute("SELECT prof_pic FROM students WHERE id = %s", (original_id,))
            result = cur.fetchone()
            if result and isinstance(result[0], bytes):
                prof_pic = result[0].decode('utf-8')  # Decode bytes to string
            else:
                prof_pic = result[0] if result else None


        print(f"Updating student with id: {update_form.id.data}")

        cur.execute("""
            UPDATE students
            SET id = %s,
                first_name = %s,
                last_name = %s,
                year_level = %s,
                course_code = %s,
                gender = %s,
                prof_pic = %s
            WHERE id = %s
        """, (
            new_id,
            update_form.first_name.data,
            update_form.last_name.data,
            update_form.year_level.data,
            update_form.course_code.data,
            update_form.gender.data,
            prof_pic
        )

        if affected_rows > 0:
            flash('Student updated successfully!', 'success')
            return redirect(url_for('students_page.students'))
        else:
            flash('Error updating student.', 'error')

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
    file = request.files.get('profile_picture')
    if file:
        upload_result = cloudinary.uploader.upload(file)
        prof_pic = str(upload_result.get('secure_url'))
        image_url = upload_result['secure_url']
        public_id = upload_result['public_id']

        # Save image_url and public_id to database here if needed

        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('your_profile_view'))

    flash("No file uploaded.", "error")
    return redirect(url_for('your_profile_view'))


@students_page.route('/delete_profile_picture/<string:cloudinary_id>', methods=['POST'])
def delete_profile_picture(cloudinary_id):
    try:
        cloudinary.uploader.destroy(cloudinary_id)

        # Remove reference in database here if needed

        flash("Profile picture deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting image: {str(e)}", "danger")

    return redirect(url_for('your_profile_view'))
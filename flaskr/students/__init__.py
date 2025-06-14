from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify, current_app
from flask_wtf.csrf import generate_csrf
from math import ceil
import cloudinary.uploader
from cloudinary.uploader import upload
from cloudinary.exceptions import Error as CloudinaryError
from . import models
from .forms import AddStudentForm, UpdateStudentForm
import json

students_page = Blueprint('students_page', __name__)

@students_page.route('/', methods=['GET', 'POST'])
def students():
    course_codes = models.get_all_course_codes()

    form = AddStudentForm()
    update_form = UpdateStudentForm()
    form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]

    if form.validate_on_submit():
        try:
            prof_pic_url = url_for('static', filename='images/default-avatar.png')
            file = request.files.get('prof_pic')
            if file and file.filename != '':
                result = upload(file)
                prof_pic_url = result.get('secure_url')

            models.insert_student(
                form.id.data.strip(),
                form.first_name.data.strip(),
                form.last_name.data.strip(),
                form.year_level.data,
                form.course_code.data,
                form.gender.data,
                prof_pic_url
            )

            flash('Student added successfully!', 'success')
            return redirect(url_for('students_page.students'))

        except CloudinaryError as e:
            flash(f"Cloudinary error: {e}", 'error')
        except Exception as e:
            flash(f"Error adding student: {e}", 'error')

    page = request.args.get('page', 1, type=int)
    rows_per_page = request.args.get('rows', 10, type=int)
    search_query = request.args.get('search', '')
    field = request.args.get('field', 'id')

    offset = (page - 1) * rows_per_page
    total_students = models.get_students_count(search_query, field)
    total_pages = ceil(total_students / rows_per_page) if rows_per_page else 1

    students = models.get_students(search_query, field, limit=rows_per_page, offset=offset)

    return render_template(
        'students/students.html',
        students=students,
        form=form,
        update_form=update_form,
        course_codes=course_codes,
        page=page,
        total_pages=total_pages,
        rows_per_page=rows_per_page,
        search_query=search_query,
        field=field
    )

@students_page.route('/search_students', methods=['GET'])
def search_students():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', 'id')
    exact = request.args.get('exact', 'false').lower() == 'true'

    print("Request path:", request.path)
    print("Search:", request.args.get("search"))
    print("Search Field:", request.args.get("search-field"))

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    try:
        results = models.search_students(query, field, exact)
        students_list = [
            {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'year_level': row[3],
                'course_code': row[4],
                'gender': row[5],
                'prof_pic': row[6]
            }
            for row in results
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

@students_page.route('/delete/<id>', methods=['POST'])
def delete_student(id):
    models.delete_student(id)
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students_page.students'))

@students_page.route('/update_students', methods=['GET', 'POST'])
def update_students():
    course_codes = models.get_all_course_codes()

    add_form = AddStudentForm()
    update_form = UpdateStudentForm()
    add_form.course_code.choices = [(code, code) for code in course_codes]
    update_form.course_code.choices = [(code, code) for code in course_codes]

    page = request.args.get('page', 1, type=int)
    rows_per_page = request.args.get('rows', 10, type=int)
    search_query = request.args.get('search', '')
    field = request.args.get('field', 'id')

    if update_form.validate_on_submit():
        original_id = request.form.get("original_id", "").strip()
        new_id = update_form.id.data.strip()

        file = request.files.get('prof_pic')
        clear_prof_pic = request.form.get("clear_prof_pic") == "1"

        current_prof_pic = models.get_student_prof_pic(original_id)
        prof_pic = current_prof_pic

        try:
            if file and file.filename:
                if current_prof_pic:
                    public_id = current_prof_pic.rsplit('/', 1)[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id)
                upload_result = cloudinary.uploader.upload(file)
                prof_pic = str(upload_result.get('secure_url'))
            elif clear_prof_pic:
                if current_prof_pic:
                    public_id = current_prof_pic.rsplit('/', 1)[-1].split('.')[0]
                    cloudinary.uploader.destroy(public_id)
                prof_pic = None
        except Exception as e:
            flash(f'Error handling profile picture: {e}', 'error')
            return redirect(url_for('students_page.students'))

        affected_rows = models.update_student(
            original_id,
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

    offset = (page - 1) * rows_per_page
    total_students = models.get_students_count(search_query, field)
    total_pages = ceil(total_students / rows_per_page) if rows_per_page else 1
    students = models.get_students(search_query, field, limit=rows_per_page, offset=offset)

    return render_template(
        'students/students.html',
        students=students,
        form=add_form,
        update_form=update_form,
        course_codes=course_codes,
        page=page,
        rows_per_page=rows_per_page,
        total_pages=total_pages,
        search_query=search_query,
        field=field
    )

@students_page.route('/upload_profile', methods=['POST'])
def upload_profile():
    file = request.files.get('profile_picture')
    if file:
        upload_result = cloudinary.uploader.upload(file)
        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('your_profile_view'))
    flash("No file uploaded.", "error")
    return redirect(url_for('your_profile_view'))

@students_page.route('/delete_profile_picture/<string:cloudinary_id>', methods=['POST'])
def delete_profile_picture(cloudinary_id):
    try:
        cloudinary.uploader.destroy(cloudinary_id)
        flash("Profile picture deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting image: {str(e)}", "danger")
    return redirect(url_for('your_profile_view'))

@students_page.route('/get_csrf_token') 
def get_csrf_token():
    return jsonify({'csrf_token': generate_csrf()})

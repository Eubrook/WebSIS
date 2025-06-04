from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify
import json
from .forms import AddCourseForm, UpdateCourseForm
from .models import (
    get_college_codes,
    college_exists,
    course_exists,
    insert_course,
    fetch_courses,
    search_courses_by_field,
    delete_course_by_code,
    update_course
)

courses_page = Blueprint('courses_page', __name__)

@courses_page.route('/courses', methods=['GET', 'POST'])
def courses():
    college_codes = get_college_codes()

    form = AddCourseForm()
    update_form = UpdateCourseForm()
    form.college_code.choices = [(code, code) for code in college_codes]
    update_form.college_code.choices = [(code, code) for code in college_codes]

    if request.method == 'POST' and form.validate_on_submit():
        course_code = form.course_code.data
        course_name = form.course_name.data
        college_code = form.college_code.data

        if not college_exists(college_code):
            flash(f"College code '{college_code}' does not exist. Please enter a valid college code.", "error")
        elif course_exists(course_code):
            flash(f"Course with code '{course_code}' already exists.", "error")
        else:
            insert_course(course_code, course_name, college_code)
            flash('Course added successfully!', 'success')
            return redirect(url_for('courses_page.courses'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", "error")

    search_query = request.args.get('search', '')
    field = request.args.get('field', 'course_code')

    allowed_fields = ['course_code', 'course_name', 'college_code']
    if field not in allowed_fields:
        field = 'course_code'

    courses = fetch_courses(search_query, field)

    return render_template(
        'courses/courses.html',
        courses=courses,
        form=form,
        update_form=update_form,
        college_codes=college_codes
    )

@courses_page.route('/search_courses', methods=['GET'])
def search_courses():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    try:
        results = search_courses_by_field(query, field, exact)
        courses_list = [
            {'course_code': row[0], 'course_name': row[1], 'college_code': row[2]}
            for row in results
        ]
        return Response(json.dumps(courses_list), mimetype='application/json')
    except Exception as e:
        print("Error:", e)
        return Response("Error occurred", status=500)

@courses_page.route('/all_courses', methods=['GET'])
def all_courses():
    results = fetch_courses()
    courses_list = [
        {'course_code': row[0], 'course_name': row[1], 'college_code': row[2]}
        for row in results
    ]
    return jsonify(courses_list)

@courses_page.route('/courses/delete/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    delete_course_by_code(course_code)
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses_page.courses'))

@courses_page.route('/courses/update_courses', methods=['GET', 'POST'])
def update_courses():
    college_codes = get_college_codes()

    add_form = AddCourseForm()
    update_form = UpdateCourseForm()
    add_form.college_code.choices = [(code, code) for code in college_codes]
    update_form.college_code.choices = [(code, code) for code in college_codes]

    if update_form.validate_on_submit():
        original_code = request.form.get("original_course_code", "").strip()
        new_code = update_form.course_code.data.strip()
        course_name = update_form.course_name.data
        college_code = update_form.college_code.data

        affected_rows = update_course(original_code, new_code, course_name, college_code)
        if affected_rows:
            flash('Course updated successfully!', 'success')
        else:
            flash('No changes were made or course not found.', 'warning')
        return redirect(url_for('courses_page.courses'))
    else:
        flash('Error updating course.', 'error')
        print("Update form validation failed:", update_form.errors)

    courses = fetch_courses()

    return render_template(
        'courses/courses.html',
        courses=courses,
        form=add_form,
        update_form=update_form,
        college_codes=college_codes
    )

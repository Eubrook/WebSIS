from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Response, jsonify
import json
from flaskr import mysql
from .forms import AddCourseForm, UpdateCourseForm


courses_page = Blueprint('courses_page', __name__)

@courses_page.route('/courses', methods=['GET', 'POST'])
def courses():
    cur = mysql.connection.cursor()

    # Get all college codes for the datalist
    cur.execute("SELECT college_code FROM colleges")
    college_codes = [row[0] for row in cur.fetchall()]

    # Initialize forms
    form = AddCourseForm()
    update_form = UpdateCourseForm()  # <-- Add this
    form.college_code.choices = [(code, code) for code in college_codes]
    update_form.college_code.choices = [(code, code) for code in college_codes]

    # Handle POST (form submission)
    if request.method == 'POST' and form.validate_on_submit():
        if form.validate_on_submit():
            course_code = form.course_code.data
            course_name = form.course_name.data
            college_code = form.college_code.data

            # Check if college_code exists in colleges table
            cur.execute(""
            "SELECT 1 FROM colleges WHERE college_code = %s", (college_code,))
            college_exists = cur.fetchone()

            if not college_exists:
                flash(f"College code '{college_code}' does not exist. Please enter a valid college code.", "error")
            else:
                # Check for duplicate course_code before insert
                cur.execute("SELECT * FROM courses WHERE course_code = %s", (course_code,))
                existing_course = cur.fetchone()

                if existing_course:
                    flash(f"Course with code '{course_code}' already exists.", "error")
                else:
                    # Proceed with insert
                    cur.execute("""
                        INSERT INTO courses (course_code, course_name, college_code)
                        VALUES (%s, %s, %s)
                    """, (course_code, course_name, college_code))
                    mysql.connection.commit()
                    flash('Course added successfully!', 'success')
                    return redirect(url_for('courses_page.courses'))
        else:
            # Flash form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", "error")
        
    # Handle GET (including search)
    search_query = request.args.get('search', '')
    field = request.args.get('field', 'course_code')

    # Protect against SQL injection in search field
    allowed_fields = ['course_code', 'course_name', 'college_code']
    if field not in allowed_fields:
        field = 'course_code'

    if search_query:
        cur.execute(f"SELECT * FROM courses WHERE {field} LIKE %s", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM courses")

    courses = cur.fetchall()
    cur.close()

    return render_template('courses/courses.html', courses=courses, form=form, update_form=update_form, college_codes=college_codes)




@courses_page.route('/search_courses', methods=['GET'])
def search_courses():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'  # Convert to Boolean

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    cur = mysql.connection.cursor()

    # Exact match or partial match handling
    if exact:
        sql = f"SELECT course_code, course_name, college_code FROM courses WHERE {field} = %s"
        params = (query,)
    else:
        sql = f"SELECT course_code, course_name, college_code FROM courses WHERE {field} LIKE %s"
        params = (f"%{query}%",)

    try:
        cur.execute(sql, params)
        courses_data = cur.fetchall()
        cur.close()

        courses_list = [
            {
                'course_code': course[0],
                'course_name': course[1],
                'college_code': course[2],
            }
            for course in courses_data
        ]

        print(courses_list)

        return Response(json.dumps(courses_list), mimetype='application/json')
    except Exception as e:
        print("Error:", e)
        return Response("Error occurred", status=500)


@courses_page.route('/all_courses', methods=['GET'])
def all_courses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_code, course_name, college_code FROM courses")
    courses_data = cur.fetchall()
    cur.close()

    courses_list = [
        {
            'course_code': course[0],
            'course_name': course[1],
            'college_code': course[2],
        }
        for course in courses_data
    ]
    
    return jsonify(courses_list)


@courses_page.route('/courses/delete/<string:course_code>', methods=['POST'])
def delete_course(course_code):
    # deletion logic here
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM courses WHERE course_code = %s", (course_code,))
    mysql.connection.commit()
    cur.close()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses_page.courses'))



@courses_page.route('/courses/update_courses', methods=['GET', 'POST'])
def update_courses():
    cur = mysql.connection.cursor()

    # Get all course codes
    cur.execute("SELECT college_code FROM colleges")
    college_codes = [row[0] for row in cur.fetchall()]

    # Initialize forms first
    add_form = AddCourseForm()
    update_form = UpdateCourseForm()

    # Then assign choices
    add_form.college_code.choices = [(code, code) for code in college_codes]
    update_form.college_code.choices = [(code, code) for code in college_codes]

    if update_form.validate_on_submit():
        original_course_code = request.form.get("original_course_code", "").strip()
        new_course_code = update_form.course_code.data.strip()
        print(f"Updating course with original_course_code: {update_form.course_code.data}")
        cur.execute("""
            UPDATE courses
            SET course_code = %s,
                course_name = %s,
                college_code = %s
            WHERE course_code = %s
        """, (
            new_course_code,
            update_form.course_name.data,
            update_form.college_code.data,
            original_course_code  # Use original_course_code here
        ))
        affected_rows = cur.rowcount
        print(f"Rows affected by update: {affected_rows}")
        mysql.connection.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses_page.courses'))  # Redirect after successful POST
    else:
        print("Update form validation failed:", update_form.errors)
        flash('Error updating course.', 'error')

        #  Fetch students so the template can render properly
        cur.execute("SELECT * FROM courses")
        courses = cur.fetchall()
        cur.close()

    return render_template(
        'courses/courses.html',
        courses=courses,
        form=add_form,
        update_form=update_form,
        college_codes=college_codes
    )



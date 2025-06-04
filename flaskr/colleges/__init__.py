from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, jsonify
import json
from flaskr import mysql
from .forms import AddCollegeForm, UpdateCollegeForm
from .models import (
    get_all_colleges, get_college_by_code, insert_college,
    delete_college_by_code, update_college_by_code, search_colleges_db
)

colleges_page = Blueprint('colleges_page', __name__)

@colleges_page.route('/colleges', methods=['GET', 'POST'])
def colleges():
    form = AddCollegeForm()
    update_form = UpdateCollegeForm()
    cur = mysql.connection.cursor()

    if request.method == 'POST' and form.validate_on_submit():
        college_code = form.college_code.data.strip()
        college_name = form.college_name.data.strip()

        if get_college_by_code(college_code):
            flash(f"College with code '{college_code}' already exists.", "error")
        else:
            insert_college(college_code, college_name)
            flash('College added successfully!', 'success')
            return redirect(url_for('colleges_page.colleges'))

    # Handle GET with optional search
    search_query = request.args.get('search', '').strip()
    field = request.args.get('field', 'college_code')

    if field not in ['college_code', 'college_name']:
        field = 'college_code'

    if search_query:
        cur.execute(f"SELECT * FROM colleges WHERE {field} LIKE %s", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM colleges")
    colleges = cur.fetchall()
    cur.close()

    return render_template(
        'colleges/colleges.html',
        colleges=colleges,
        form=form,
        update_form=update_form,
    )


@colleges_page.route('/search_colleges', methods=['GET'])
def search_colleges():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    try:
        colleges_data = search_colleges_db(field, query, exact)
        colleges_list = [{'college_code': c[0], 'college_name': c[1]} for c in colleges_data]
        return Response(json.dumps(colleges_list), mimetype='application/json')
    except Exception as e:
        print("Error in search_colleges:", e)
        return Response("Error occurred", status=500)



@colleges_page.route('/all_colleges', methods=['GET'])
def all_colleges():
    colleges_data = get_all_colleges()
    colleges_list = [{'college_code': c[0], 'college_name': c[1]} for c in colleges_data]
    return Response(json.dumps(colleges_list), mimetype='application/json')


@colleges_page.route('/colleges/delete/<string:college_code>', methods=['POST'])
def delete_college(college_code):
    delete_college_by_code(college_code)
    flash('College deleted successfully!', 'success')
    return redirect(url_for('colleges_page.colleges'))


@colleges_page.route('/colleges/update_colleges', methods=['GET', 'POST'])
def update_colleges():
    cur = mysql.connection.cursor()
    add_form = AddCollegeForm()
    update_form = UpdateCollegeForm()

    if request.method == 'POST':
        update_form.original_college_code.data = request.form.get('original_college_code')

    if update_form.validate_on_submit():
        original_code = request.form.get("original_college_code", "").strip()
        new_code = update_form.college_code.data.strip()
        new_name = update_form.college_name.data.strip()

        update_college_by_code(original_code, new_code, new_name)
        flash('College updated successfully!', 'success')
        return redirect(url_for('colleges_page.colleges'))

    if request.method == 'POST' and not update_form.validate_on_submit():
        flash('Error updating college.', 'error')

    cur.execute("SELECT * FROM colleges")
    colleges = cur.fetchall()
    cur.close()

    return render_template(
        'colleges/colleges.html',
        colleges=colleges,
        form=add_form,
        update_form=update_form,
    )

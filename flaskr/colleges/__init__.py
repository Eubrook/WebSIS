from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, session
import json
from flaskr import mysql
from .forms import AddCollegeForm

colleges_page = Blueprint('colleges_page', __name__)


@colleges_page.route('/colleges', methods=['GET', 'POST'])
def colleges():

    cur = mysql.connection.cursor()
    form = AddCollegeForm()

    # Handle POST (form submission)
    if request.method == 'POST' and form.validate_on_submit():
        college_code = form.college_code.data
        college_name = form.college_name.data

        # Check for duplicate college_code before insert
        cur.execute("SELECT * FROM colleges WHERE college_code = %s", (college_code,))
        existing_college = cur.fetchone()

        if existing_college:
            flash(f"College with code '{college_code}' already exists.", "error")
        else:
            # Proceed with insert
            cur.execute("""
                INSERT INTO colleges (college_code, college_name)
                VALUES (%s, %s)
            """, (college_code, college_name))
            mysql.connection.commit()
            flash('College added successfully!', 'success')
            return redirect(url_for('colleges_page.colleges'))

    # Handle GET (including search)
    search_query = request.args.get('search', '')
    field = request.args.get('field', 'college_code')

    # Protect against SQL injection in search field
    allowed_fields = ['college_code', 'college_name']
    if field not in allowed_fields:
        field = 'college_code'

    if search_query:
        cur.execute(f"SELECT * FROM colleges WHERE {field} LIKE %s", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM colleges")

    colleges = cur.fetchall()
    cur.close()

    return render_template('colleges/colleges.html', colleges=colleges, form=form)



@colleges_page.route('/search_colleges', methods=['GET'])
def search_colleges():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'  # Convert to Boolean

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    cur = mysql.connection.cursor()

    # Exact match or partial match handling
    if exact:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} = %s"
        params = (query,)
    else:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} LIKE %s"
        params = (f"%{query}%",)

    try:
        cur.execute(sql, params)
        colleges_data = cur.fetchall()
        cur.close()

        colleges_list = [
            {
                'college_code': college[0],
                'college_name': college[1],
            }
            for college in colleges_data
        ]

        print(colleges_list)

        return Response(json.dumps(colleges_list), mimetype='application/json')
    except Exception as e:
        print("Error:", e)
        return Response("Error occurred", status=500)

@colleges_page.route('/all_colleges', methods=['GET'])
def all_colleges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT college_code, college_name FROM colleges")
    colleges_data = cur.fetchall()
    cur.close()

    colleges_list = [
        {
            'college_code': college[0],
            'college_name': college[1],
        }
        for college in colleges_data
    ]
    
    return Response(json.dumps(colleges_list), mimetype='application/json')

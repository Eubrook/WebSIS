from flask import Blueprint, render_template, request, flash, redirect, url_for, Response, session
import json
from flaskr import mysql
from .forms import AddCollegeForm, UpdateCollegeForm

colleges_page = Blueprint('colleges_page', __name__)


@colleges_page.route('/colleges', methods=['GET', 'POST'])
def colleges():

    cur = mysql.connection.cursor()
    form = AddCollegeForm()
    update_form = UpdateCollegeForm()

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

    return render_template('colleges/colleges.html', colleges=colleges, form=form, update_form=update_form)



@colleges_page.route('/search_colleges', methods=['GET'])
def search_colleges():
    query = request.args.get('query', '').strip()
    field = request.args.get('field', '')
    exact = request.args.get('exact', 'false').lower() == 'true'

    if not query or not field:
        return Response(json.dumps([]), mimetype='application/json')

    cur = mysql.connection.cursor()

    try:
        if exact:
            sql = f"""
                SELECT college_code, college_name 
                FROM colleges 
                WHERE {field} = %s
            """
            cur.execute(sql, (query,))
        else:
            sql = f"""
                SELECT college_code, college_name 
                FROM colleges 
                WHERE {field} LIKE %s OR {field} LIKE %s
            """
            cur.execute(sql, (f"{query}%", f"% {query}%"))

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

    except Exception as e:
        print("Error in search_colleges:", e)
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



@colleges_page.route('/colleges/delete/<string:college_code>', methods=['POST'])
def delete_college(college_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM colleges WHERE college_code = %s", (college_code,))
    mysql.connection.commit()
    cur.close()
    flash('College deleted successfully!', 'success')
    return redirect(url_for('colleges_page.colleges'))




@colleges_page.route('/colleges/update_colleges', methods=['GET', 'POST'])
def update_colleges():
    cur = mysql.connection.cursor()
    
    add_form = AddCollegeForm()
    update_form = UpdateCollegeForm()

    # Set original_college_code data for validation
    if request.method == 'POST':
        update_form.original_college_code.data = request.form.get('original_college_code')

    if update_form.validate_on_submit():

        original_college_code = request.form.get("original_college_code", "").strip()
        new_college_code = update_form.college_code.data.strip()
        
        print(f"Updating college with original_college_code: {update_form.original_college_code.data}")
        cur.execute("""
            UPDATE colleges
            SET college_code = %s,
                college_name = %s
            WHERE college_code = %s
        """, (
                new_college_code,
                update_form.college_name.data,
                original_college_code
        ))
        affected_rows = cur.rowcount
        print(f"Rows affected by update: {affected_rows}")
        mysql.connection.commit()
        cur.close()
        flash('College updated successfully!', 'success')
        return redirect(url_for('colleges_page.colleges'))  # Redirect after successful POST
    else:
        if request.method == 'POST':
            flash('Error updating college.', 'error')

        # Fetch colleges so the template can render properly
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM colleges")
        colleges = cur.fetchall()
        cur.close()
   
    return render_template(
        'colleges/colleges.html',
        colleges=colleges,
        form=add_form,
        update_form=update_form
    )

# courses/models.py

from flaskr import mysql

def get_college_codes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT college_code FROM colleges")
    college_codes = [row[0] for row in cur.fetchall()]
    cur.close()
    return college_codes

def college_exists(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM colleges WHERE college_code = %s", (college_code,))
    result = cur.fetchone()
    cur.close()
    return result is not None

def course_exists(course_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses WHERE course_code = %s", (course_code,))
    result = cur.fetchone()
    cur.close()
    return result is not None

def insert_course(course_code, course_name, college_code):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO courses (course_code, course_name, college_code)
        VALUES (%s, %s, %s)
    """, (course_code, course_name, college_code))
    mysql.connection.commit()
    cur.close()

def fetch_courses(search_query=None, field='course_code'):
    cur = mysql.connection.cursor()
    if search_query:
        cur.execute(f"SELECT * FROM courses WHERE {field} LIKE %s", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    cur.close()
    return courses

def search_courses_by_field(query, field, exact=False):
    cur = mysql.connection.cursor()
    if exact:
        sql = f"SELECT course_code, course_name, college_code FROM courses WHERE {field} = %s"
        cur.execute(sql, (query,))
    else:
        sql = f"SELECT course_code, course_name, college_code FROM courses WHERE {field} LIKE %s"
        cur.execute(sql, (f"%{query}%",))
    results = cur.fetchall()
    cur.close()
    return results

def delete_course_by_code(course_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM courses WHERE course_code = %s", (course_code,))
    mysql.connection.commit()
    cur.close()

def update_course(original_code, new_code, course_name, college_code):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE courses
        SET course_code = %s,
            course_name = %s,
            college_code = %s
        WHERE course_code = %s
    """, (new_code, course_name, college_code, original_code))
    mysql.connection.commit()
    affected_rows = cur.rowcount
    cur.close()
    return affected_rows

def is_course_name_duplicate(course_name, exclude_code=None):
    cur = mysql.connection.cursor()
    if exclude_code:
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_name = %s AND course_code != %s", (course_name, exclude_code))
    else:
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_name = %s", (course_name,))
    result = cur.fetchone()
    cur.close()
    return result[0] > 0

def is_course_code_duplicate(course_code, exclude_code=None):
    cur = mysql.connection.cursor()
    if exclude_code:
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s AND course_code != %s", (course_code, exclude_code))
    else:
        cur.execute("SELECT COUNT(*) FROM courses WHERE course_code = %s", (course_code,))
    result = cur.fetchone()
    cur.close()
    return result[0] > 0

from flaskr import mysql


def get_all_course_codes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_code FROM courses")
    course_codes = [row[0] for row in cur.fetchall()]
    cur.close()
    return course_codes

def insert_student(student_id, first_name, last_name, year_level, course_code, gender, prof_pic):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO students (id, first_name, last_name, year_level, course_code, gender, prof_pic)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (student_id, first_name, last_name, year_level, course_code, gender, prof_pic))
    mysql.connection.commit()
    cur.close()


def get_students_count(search_query='', field='id'):
    cur = mysql.connection.cursor()

    if search_query:
        query = f"SELECT COUNT(*) FROM students WHERE {field} LIKE %s"
        cur.execute(query, (f"%{search_query}%",))
    else:
        query = "SELECT COUNT(*) FROM students"
        cur.execute(query)

    count = cur.fetchone()[0]
    cur.close()
    return count




def search_students(query, field, exact=False):
    allowed_fields = ['id', 'first_name', 'last_name', 'year_level', 'course_code', 'gender']
    if field not in allowed_fields or not query:
        return []

    cur = mysql.connection.cursor()
    if exact:
        sql = f"SELECT id, first_name, last_name, year_level, course_code, gender FROM students WHERE {field} = %s"
        cur.execute(sql, (query,))
    else:
        sql = f"SELECT id, first_name, last_name, year_level, course_code, gender FROM students WHERE {field} LIKE %s"
        cur.execute(sql, (f"%{query}%",))
    results = cur.fetchall()
    cur.close()

    return results

def get_students(search_query='', field='id', limit=None, offset=0):
    cur = mysql.connection.cursor()

    if search_query:
        query = f"""
            SELECT id, first_name, last_name, year_level, course_code, gender, prof_pic 
            FROM students 
            WHERE {field} LIKE %s 
            ORDER BY id
        """
        params = [f"%{search_query}%"]
    else:
        query = """
            SELECT id, first_name, last_name, year_level, course_code, gender, prof_pic 
            FROM students 
            ORDER BY id
        """
        params = []

    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

    cur.execute(query, tuple(params))
    students = cur.fetchall()
    cur.close()
    return students



def delete_student(student_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
    mysql.connection.commit()
    cur.close()

def get_student_prof_pic(student_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT prof_pic FROM students WHERE id = %s", (student_id,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def update_student(original_id, new_id, first_name, last_name, year_level, course_code, gender, prof_pic):
    cur = mysql.connection.cursor()
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
    """, (new_id, first_name, last_name, year_level, course_code, gender, prof_pic, original_id))
    affected_rows = cur.rowcount
    mysql.connection.commit()
    cur.close()
    return affected_rows

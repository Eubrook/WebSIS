from flaskr import mysql


def get_college_by_code(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges WHERE college_code = %s", (college_code,))
    result = cur.fetchone()
    cur.close()
    return result


def insert_college(college_code, college_name):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO colleges (college_code, college_name)
        VALUES (%s, %s)
    """, (college_code, college_name))
    mysql.connection.commit()
    cur.close()


def delete_college_by_code(college_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM colleges WHERE college_code = %s", (college_code,))
    mysql.connection.commit()
    cur.close()


def update_college_by_code(original_code, new_code, new_name):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE colleges
        SET college_code = %s, college_name = %s
        WHERE college_code = %s
    """, (new_code, new_name, original_code))
    mysql.connection.commit()
    cur.close()


def get_all_colleges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT college_code, college_name FROM colleges")
    data = cur.fetchall()
    cur.close()
    return data


def search_colleges_db(field, query, exact=False):
    cur = mysql.connection.cursor()
    if exact:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} = %s"
        cur.execute(sql, (query,))
    else:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} LIKE %s OR {field} LIKE %s"
        cur.execute(sql, (f"{query}%", f"% {query}%"))
    result = cur.fetchall()
    cur.close()
    return result

from flaskr import mysql


def get_college_by_code(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges WHERE college_code = %s", (college_code,))
    result = cur.fetchone()
    cur.close()
    return result


def insert_college(college_code, college_name):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO colleges (college_code, college_name)
        VALUES (%s, %s)
    """, (college_code, college_name))
    mysql.connection.commit()
    cur.close()


def delete_college_by_code(college_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM colleges WHERE college_code = %s", (college_code,))
    mysql.connection.commit()
    cur.close()


def update_college_by_code(original_code, new_code, new_name):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE colleges
        SET college_code = %s, college_name = %s
        WHERE college_code = %s
    """, (new_code, new_name, original_code))
    mysql.connection.commit()
    cur.close()


def get_all_colleges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT college_code, college_name FROM colleges")
    data = cur.fetchall()
    cur.close()
    return data


def search_colleges_db(field, query, exact=False):
    cur = mysql.connection.cursor()
    if exact:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} = %s"
        cur.execute(sql, (query,))
    else:
        sql = f"SELECT college_code, college_name FROM colleges WHERE {field} LIKE %s OR {field} LIKE %s"
        cur.execute(sql, (f"{query}%", f"% {query}%"))
    result = cur.fetchall()
    cur.close()
    return result


def college_exists(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM colleges WHERE college_code = %s", (college_code,))
    result = cur.fetchone()
    cur.close()
    return result[0] > 0


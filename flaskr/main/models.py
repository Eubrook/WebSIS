from flaskr import mysql

def get_all_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.close()
    return students

def get_all_colleges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges")
    colleges = cur.fetchall()
    cur.close()
    return colleges

def get_all_courses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    cur.close()
    return courses

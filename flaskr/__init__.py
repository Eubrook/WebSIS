from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flaskr.mysql__init__ import create_db
from flask_bootstrap import Bootstrap
from flask import current_app
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_API_UPLOAD_PRESET 




db_url = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}" 
mysql = MySQL()
bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)

    create_db()  # Call create_db() function before initializing the app

    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['MYSQL_HOST'] = DB_HOST
    app.config['MYSQL_USER'] = DB_USERNAME
    app.config['MYSQL_PASSWORD'] = DB_PASSWORD
    app.config['MYSQL_DB'] = DB_NAME
    app.config['CLOUDINARY_CLOUD_NAME'] = CLOUDINARY_CLOUD_NAME
    app.config['CLOUDINARY_API_KEY'] = CLOUDINARY_API_KEY
    app.config['CLOUDINARY_API_SECRET'] = CLOUDINARY_API_SECRET
    app.config['CLOUDINARY_API_UPLOAD_PRESET'] = CLOUDINARY_API_UPLOAD_PRESET 
 
    mysql.init_app(app)
    CSRFProtect(app)

    from .colleges import colleges_page
    from .students import students_page
    from .courses import courses_page

    app.register_blueprint(colleges_page, url_prefix='/')
    app.register_blueprint(students_page, url_prefix='/')
    app.register_blueprint(courses_page, url_prefix='/')

    
    bootstrap.init_app(app)

    def get_all_students():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM students')
        students = cur.fetchall()
        cur.close()
        return students

    def get_all_colleges():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM colleges')
        colleges = cur.fetchall()
        cur.close()
        return colleges

    def get_all_courses():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM courses')
        courses = cur.fetchall()
        cur.close()
        return courses

    
    @app.route('/')
    def main_page():
        students = get_all_students()
        colleges = get_all_colleges()
        courses = get_all_courses()
        total_students = len(students)
        total_colleges = len(colleges)
        total_courses = len(courses)
        return render_template('home.html', students=students, colleges=colleges, courses=courses,
                                total_students=total_students, total_colleges=total_colleges, total_courses=total_courses)

    
    @app.route('/students')
    def students():
        return render_template('students/students.html', cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'], 
                                upload_preset=current_app.config['CLOUDINARY_API_UPLOAD_PRESET'])
    
    @app.route('/colleges')
    def colleges():
        return render_template('colleges/colleges.html')
    
    @app.route('/courses')
    def courses():
        return render_template('courses/courses.html')
    
 
    return app

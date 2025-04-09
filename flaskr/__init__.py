from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flaskr.mysql__init__ import create_db
from flask_bootstrap import Bootstrap
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY 
# BOOTSTRAP_SERVE_LOCAL



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
 
    mysql.init_app(app)
    CSRFProtect(app)

    from .colleges import colleges_page
    from .students import students_page
    from .courses import courses_page

    app.register_blueprint(colleges_page, url_prefix='/')
    app.register_blueprint(students_page, url_prefix='/')
    app.register_blueprint(courses_page, url_prefix='/')

    
    bootstrap.init_app(app)

    @app.route('/')
    def main_page():
        return render_template('home.html')
    
    @app.route('/students')
    def students():
        return render_template('students/students.html')
    
    @app.route('/colleges')
    def colleges():
        return render_template('colleges/colleges.html')
    
    @app.route('/courses')
    def courses():
        return render_template('courses/courses.html')
    
 
    return app

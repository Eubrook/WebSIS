from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from flaskr.mysql__init__ import create_db
from config import (
    DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY,
    CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET,
    CLOUDINARY_API_UPLOAD_PRESET
)
import cloudinary

mysql = MySQL()
bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)

    # Ensure DB exists
    create_db()

    # App config
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['MYSQL_HOST'] = DB_HOST
    app.config['MYSQL_USER'] = DB_USERNAME
    app.config['MYSQL_PASSWORD'] = DB_PASSWORD
    app.config['MYSQL_DB'] = DB_NAME
    app.config['CLOUDINARY_CLOUD_NAME'] = CLOUDINARY_CLOUD_NAME
    app.config['CLOUDINARY_API_KEY'] = CLOUDINARY_API_KEY
    app.config['CLOUDINARY_API_SECRET'] = CLOUDINARY_API_SECRET
    app.config['CLOUDINARY_API_UPLOAD_PRESET'] = CLOUDINARY_API_UPLOAD_PRESET

    # Initialize extensions
    mysql.init_app(app)
    CSRFProtect(app)
    bootstrap.init_app(app)

    # Configure cloudinary globally
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

    # Import and register blueprints here
    from .main import main_page
    from .students import students_page
    from .colleges import colleges_page
    from .courses import courses_page

    app.register_blueprint(main_page, url_prefix='/')
    app.register_blueprint(students_page, url_prefix='/students')
    app.register_blueprint(colleges_page, url_prefix='/colleges')
    app.register_blueprint(courses_page, url_prefix='/courses')


    for rule in app.url_map.iter_rules():
        print(rule)


    return app

from config import DB_HOST, DB_PASSWORD, DB_USERNAME, DB_NAME
import mysql.connector

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD
)

cursor = db.cursor()

def create_db():
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        # Create colleges table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS colleges (
            college_code VARCHAR(20) NOT NULL,
            college_name VARCHAR(80) NOT NULL,
            PRIMARY KEY (college_code),
            UNIQUE (college_name)
        )
        """)
        
        # Create courses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_code VARCHAR(20) NOT NULL,
            course_name VARCHAR(80) NOT NULL,
            college_code VARCHAR(20),
            PRIMARY KEY (course_code),
            UNIQUE (course_name),
            FOREIGN KEY (college_code) REFERENCES colleges(college_code) ON DELETE SET NULL ON UPDATE CASCADE
        )
        """)
        
        # Create students table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id CHAR(10) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            year_level INT NOT NULL, 
            course_code VARCHAR(10),
            gender CHAR(6) NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE SET NULL ON UPDATE CASCADE
        )
        """)
        
        db.commit()
        print("Database created successfully!")
    except mysql.connector.Error as error:
        print("Error creating database: ", error)

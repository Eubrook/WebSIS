from flask import Blueprint, render_template
from .models import get_all_students, get_all_colleges, get_all_courses

main_page = Blueprint('main_page', __name__)

@main_page.route('/')
def home():
    students = get_all_students()
    colleges = get_all_colleges()
    courses = get_all_courses()

    return render_template(
        'home.html',
        students=students,
        colleges=colleges,
        courses=courses,
        total_students=len(students),
        total_colleges=len(colleges),
        total_courses=len(courses)
    )

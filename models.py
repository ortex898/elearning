
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student or instructor
    
    # Profile fields
    full_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    school = db.Column(db.String(255))
    grade = db.Column(db.String(20))  # For students
    subjects = db.Column(db.Text)  # For instructors
    teacher_id = db.Column(db.String(50))  # For instructors

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(255), nullable=False)
    instructor_id = db.Column(db.String(32), db.ForeignKey('users.id'))
    grade = db.Column(db.String(20))
    description = db.Column(db.Text)

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    student_id = db.Column(db.String(32), db.ForeignKey('users.id'))
    course_id = db.Column(db.String(32), db.ForeignKey('courses.id'))

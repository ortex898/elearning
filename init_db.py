
from app import app, db
from models import User, Course, Enrollment
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create sample users
        admin = User(
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            user_type='instructor',
            full_name='Admin User',
            school='Secret Coder Academy'
        )
        
        student = User(
            email='student@example.com',
            password=generate_password_hash('student123'),
            user_type='student',
            full_name='Student User',
            school='Secret Coder Academy',
            grade='10th'
        )
        
        db.session.add_all([admin, student])
        db.session.commit()
        
        # Create sample courses
        course = Course(
            name='Introduction to Python',
            instructor_id=admin.id,
            description='Learn Python basics',
            grade='10th',
            price=99.99,
            is_free=False,
            level='Beginner'
        )
        
        db.session.add(course)
        db.session.commit()
        
        # Create sample enrollment
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id
        )
        
        db.session.add(enrollment)
        db.session.commit()

if __name__ == '__main__':
    init_db()

import os
from flask import Flask, request, jsonify, session, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Course, Enrollment
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # For debugging

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    user_type = data.get('userType', '')

    if not email or not password or not user_type:
        return jsonify({'error': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(
        email=data['email'],
        password=hashed_password,
        user_type=data['userType']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'id': new_user.id,
        'email': new_user.email,
        'userType': new_user.user_type
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        return jsonify({
            'id': user.id,
            'email': user.email,
            'userType': user.user_type,
            'profile': {
                'fullName': user.full_name,
                'phone': user.phone,
                'school': user.school,
                'grade': user.grade,
                'subjects': user.subjects,
                'teacherId': user.teacher_id
            }
        })

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    data = request.json

    for key, value in data.items():
        setattr(user, key, value)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/dashboard/<user_type>/<user_id>')
def dashboard(user_type, user_id):
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(user_id)
    if not user:
        return redirect('/login')

    if user_type == 'student':
        enrollments = Enrollment.query.filter_by(student_id=user_id).all()
        courses = [Course.query.get(e.course_id) for e in enrollments]
        return render_template('student_dashboard.html', user=user, courses=courses)
    else:
        courses = Course.query.filter_by(instructor_id=user_id).all()
        return render_template('instructor_dashboard.html', user=user, courses=courses)

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'price': c.price,
        'is_free': c.is_free,
        'image_url': c.image_url,
        'rating': c.rating,
        'learners_count': c.learners_count,
        'level': c.level
    } for c in courses])

@app.route('/api/courses', methods=['POST'])
def create_course():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    new_course = Course(
        name=data['name'],
        description=data.get('description', ''),
        instructor_id=session['user_id'],
        price=data.get('price', 0.0),
        is_free=data.get('is_free', True),
        image_url=data.get('image_url', ''),
        level=data.get('level', 'Beginner')
    )

    db.session.add(new_course)
    db.session.commit()

    return jsonify({
        'id': new_course.id,
        'name': new_course.name,
        'description': new_course.description
    })

@app.route('/api/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    return jsonify({
        'id': course.id,
        'name': course.name,
        'description': course.description,
        'price': course.price,
        'is_free': course.is_free,
        'image_url': course.image_url,
        'rating': course.rating,
        'learners_count': course.learners_count,
        'level': course.level
    })

@app.route('/api/enroll/<course_id>', methods=['POST'])
def enroll_course(course_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    enrollment = Enrollment(
        student_id=session['user_id'],
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({'message': 'Enrolled successfully'})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/single')
def single():
    return render_template('single.html')

@app.route('/student/profile')
def student_profile():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('student_profile.html', user=user)

@app.route('/instructor/profile')
def instructor_profile():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('instructor_profile.html', user=user)

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('instructor_dashboard.html', user=user)

@app.route('/instructor/classes')
def instructor_classes():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('instructor_classes.html', user=user)

@app.route('/instructor/settings')
def instructor_settings():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('instructor_settings.html', user=user)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('student_dashboard.html', user=user)

@app.route('/student/courses')
def student_courses():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('student_courses.html', user=user)

@app.route('/student/assignments')
def student_assignments():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('student_assignments.html', user=user)

@app.route('/student/grades')
def student_grades():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('student_grades.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
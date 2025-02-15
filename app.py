
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Course, Enrollment
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
        
    hashed_password = generate_password_hash(data['password'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

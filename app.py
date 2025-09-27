from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, desc # Import necessary SQLAlchemy functions

# --- 1. Configuration ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://postgres:flicksbystella@localhost:5432/course_recommendations_db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)  # Allows React frontend to communicate with API

# ----------------------------------------------------------------------
# --- 2. Database Models (Define Table Structure) ---
# ----------------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    major = db.Column(db.String(100))
    # Relationship to Enrollment (one user has many enrollments)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer)
    # Relationship to Enrollment (one course has many enrollments)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.String(50))
    grade = db.Column(db.String(5)) 
    
# ----------------------------------------------------------------------
# --- 3. RESTful API Endpoints ---
# ----------------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    """Basic test route to confirm the API is live."""
    return jsonify({"message": "Course Recommendation API is running!"})

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Retrieves a list of all courses for the frontend catalog/search."""
    courses = db.session.execute(db.select(Course)).scalars().all()
    
    # Format the data into a list of dictionaries for JSON response
    course_list = [{
        'id': course.id,
        'title': course.title,
        'department': course.department,
        'description': course.description,
        'credits': course.credits
    } for course in courses]
    
    return jsonify(course_list)

@app.route('/api/data/trends', methods=['GET'])
def get_enrollment_trends():
    """Retrieves aggregated data (e.g., popularity by department) for the dashboard."""
    
    # Query: Count enrollments per department, ordered by most popular
    results = db.session.query(
        Course.department,
        func.count(Enrollment.id).label('enrollment_count')
    ).join(Enrollment).group_by(Course.department).order_by(desc('enrollment_count')).all()

    # Format data for frontend visualization
    trend_data = {
        'departments': [res.department for res in results],
        'counts': [res.enrollment_count for res in results]
    }
    
    return jsonify({"message": "Enrollment trend data retrieved successfully.", "data": trend_data})

# ----------------------------------------------------------------------
# --- 4. Application Runner ---
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Runs the Flask server on port 5000 (standard for local backend API)
    app.run(debug=True, port=5000)
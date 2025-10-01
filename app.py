from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, desc
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

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
    ).join(Enrollment).group_by(
        Course.department
    ).order_by(
        desc('enrollment_count')
    ).all()

    # Format data for frontend visualization
    trends_list = [
        {'department': res.department, 'average_enrollment': res.enrollment_count} 
        for res in results
    ]

    return jsonify(trends_list)

# app.py (After get_enrollment_trends)

def get_recommendations_logic(user_id, num_recommendations=5):
    """
    Core logic for generating collaborative filtering recommendations.
    Uses pandas and scikit-learn for matrix factorization and similarity.
    """
    try:
        results = db.session.query(
            Enrollment.user_id, 
            Enrollment.course_id
        ).all()
        
        enrollment_data = [{
            'user_id': r[0], 
            'course_id': r[1]
        } for r in results]

        enrollment_df = pd.DataFrame(enrollment_data)
        enrollment_df['rating'] = 1 
    
        # 3. Create the User-Course Matrix (Pivot table)
        # Use 1 for 'enrolled' to indicate a rating/interaction
        user_course_matrix = enrollment_df.pivot_table(
            index='user_id', 
            columns='course_id', 
            values='rating', # Use any column here, we just care about presence
            aggfunc='count', # Count occurrences (will be 1 for unique enrollment)
            fill_value=0
        )
        
        # Handle the case where the requested user_id is not in the matrix
        if user_id not in user_course_matrix.index:
            return [] # Cannot recommend for unknown user
        
        if user_course_matrix.loc[user_id].sum() == 0:
            return [] #
            
        # 4. Calculate User Similarity (using Cosine Similarity)
        # We transpose the matrix to get a Course-User matrix for calculating similarity
        user_similarity = cosine_similarity(user_course_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, 
        index=user_course_matrix.index, 
        columns=user_course_matrix.index)

        # 5. Get the user's index and similarity scores
        user_index = user_course_matrix.index.get_loc(user_id)
        
        # Get the similarity scores for the target user (excluding the user themselves)
        similar_users = user_similarity_df.iloc[user_index].sort_values(ascending=False).drop(user_id)        
        # Simple recommendation: Find courses rated by similar users that the target user hasn't taken
        
        # Get the courses the target user has already taken (value > 0)
        taken_courses = user_course_matrix.loc[user_id][user_course_matrix.loc[user_id] > 0].index.tolist()
        
        recommendations = []
        
        # Iterate through similar users to find new courses
        for similar_user_id, similarity_score in similar_users.items():
            if similarity_score <= 0: # Stop if similarity is zero
                break

            # Courses taken by the similar user
            similar_user_courses = user_course_matrix.loc[similar_user_id][user_course_matrix.loc[similar_user_id] > 0].index.tolist()
            
            # Find new courses to recommend (courses similar user took - courses target user took)
            new_courses = [course_id for course_id in similar_user_courses if course_id not in taken_courses]
            
            # Add them to the recommendations list
            for course_id in new_courses:
                if course_id not in [rec['id'] for rec in recommendations]:
                    recommendations.append({'id': course_id, 'score': similarity_score})
            
            if len(recommendations) >= num_recommendations * 2: # Get more than needed initially
                break

        # Sort by score and take the top N unique courses
        recommendations_df = pd.DataFrame(recommendations).sort_values(by='score', ascending=False).drop_duplicates(subset=['id']).head(num_recommendations)
        
        recommended_course_ids = recommendations_df['id'].tolist()
        
        return recommended_course_ids

    except Exception as e:
        print(f"Error during recommendation logic: {e}")
        return []

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Retrieves course recommendations for a given user ID."""
    
    # 1. Run the recommendation logic to get the course IDs
    recommended_ids = get_recommendations_logic(user_id)

    if not recommended_ids:
        return jsonify({"message": "No recommendations found (User may not exist or database is sparse).", "courses": []}), 200

    # 2. Fetch full course details for the recommended IDs
    # This ensures the frontend gets Title, Department, etc.
    CourseModel = db.Model.metadata.tables['course']
    
    # Use IN clause to select multiple courses by ID
    courses = db.session.execute(
        db.select(CourseModel).where(CourseModel.c.id.in_(recommended_ids))
    ).fetchall()

    # 3. Format the results for JSON
    recommended_courses = []
    for course in courses:
        recommended_courses.append({
            'id': course.id,
            'title': course.title,
            'department': course.department,
            'description': course.description,
            'credits': course.credits
        })
        
    return jsonify({
        "message": f"Successfully retrieved {len(recommended_courses)} recommendations for user {user_id}.",
        "courses": recommended_courses
    })

# ----------------------------------------------------------------------
# --- 4. Application Runner ---
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Runs the Flask server on port 5000 (standard for local backend API)
    app.run(debug=True, port=5000)
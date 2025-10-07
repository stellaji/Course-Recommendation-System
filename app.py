from flask import Flask, jsonify, request
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
    title = db.Column(db.String(500), nullable=False)
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

def generate_recommendations_for_input(taken_course_ids, num_recommendations=4):
    """
    Core logic modified to generate recommendations based on a list of input course IDs 
    (instead of a specific user_id in the database).
    """
    if len(taken_course_ids) == 0:
        return []

    try:
        # 1. Fetch ALL enrollment data to build the similarity matrix
        results = db.session.query(
            Enrollment.user_id, 
            Enrollment.course_id
        ).all()
        
        enrollment_data = [{
            'user_id': r[0], 
            'course_id': r[1]
        } for r in results]

        enrollment_df = pd.DataFrame(enrollment_data)

        # 2. Create the User-Course Matrix from existing database data
        enrollment_df['rating'] = 1 
        
        user_course_matrix = enrollment_df.pivot_table(
            index='user_id', 
            columns='course_id', 
            values='rating',
            aggfunc='count',
            fill_value=0
        )
        
        # 3. Create a 'Virtual User' Row
        
        # Start with a zero vector for the new user, aligned with existing courses
        # Use a non-conflicting index, like 0
        new_user_vector = pd.Series(0, index=user_course_matrix.columns, name=0)
        
        # Mark the courses the new user has taken (input courses) with a 1
        for course_id in taken_course_ids:
            if course_id in new_user_vector.index:
                new_user_vector.loc[course_id] = 1
        
        # Add the new user vector to the matrix for calculation
        # Use .append() or pd.concat() depending on your pandas version
        try:
            full_matrix = pd.concat([new_user_vector.to_frame().T, user_course_matrix], ignore_index=False)
        except AttributeError:
             # Fallback for older pandas versions
             full_matrix = user_course_matrix._append(new_user_vector.to_frame().T)

        
        # Fill any missing columns/NaNs that resulted from the merge with 0
        full_matrix = full_matrix.fillna(0) 

        # 4. Calculate Similarity (Now includes the new user (index 0))
        user_similarity = cosine_similarity(full_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, 
                                          index=full_matrix.index, 
                                          columns=full_matrix.index)
        
        # The new user is always the first entry after the merge
        new_user_id = full_matrix.index[0]

        # Get similarity scores for the new user (excluding the new user themselves)
        similar_users = user_similarity_df.loc[new_user_id].sort_values(ascending=False).drop(new_user_id)
        
        # 5. Generate Recommendations
        recommendations = []
        
        for similar_user_id, similarity_score in similar_users.items():
            if similarity_score <= 0 or len(recommendations) >= num_recommendations * 2:
                break

            # Courses taken by the similar user (from the full matrix)
            similar_user_courses = full_matrix.loc[similar_user_id][full_matrix.loc[similar_user_id] > 0].index.tolist()
            
            # Find new courses to recommend (courses similar user took - courses new user took)
            new_courses = [course_id for course_id in similar_user_courses if course_id not in taken_course_ids]
            
            for course_id in new_courses:
                # Ensure we only add unique courses to the final list
                if course_id not in [rec['id'] for rec in recommendations]:
                    # We score by the similarity score of the user who took it
                    recommendations.append({'id': course_id, 'score': similarity_score})

        # 6. Final Selection
        # Sort by score and take the top N unique courses
        if not recommendations:
            return []
            
        recommendations_df = pd.DataFrame(recommendations).sort_values(
            by='score', 
            ascending=False
        ).drop_duplicates(
            subset=['id']
        ).head(num_recommendations)
        
        return recommendations_df['id'].tolist()

    except Exception as e:
        # Log the error and return empty list
        print(f"Error during on-the-fly recommendation logic: {e}") 
        return []

@app.route('/api/recommend', methods=['POST'])
def recommend_for_virtual_user():
    """
    Accepts user input (taken courses, major, etc.) and generates 
    on-the-fly recommendations without saving a new user to the database.
    """
    data = request.get_json()
    
    # Extract the necessary data
    taken_course_ids = data.get('taken_course_ids', [])
    num_to_recommend = 4 # Fixed requirement from user

    if len(taken_course_ids) < 2:
        return jsonify({"message": "Please select at least two courses taken to generate recommendations.", "courses": []}), 400

    # 1. Run the new recommendation logic
    recommended_ids = generate_recommendations_for_input(taken_course_ids, num_to_recommend)

    if not recommended_ids:
        # Fallback for very sparse or edge cases
        return jsonify({"message": "No specific recommendations found. Try selecting different courses.", "courses": []}), 200

    # 2. Fetch full course details for the recommended IDs
    CourseModel = db.Model.metadata.tables['course']
    
    courses = db.session.execute(
        db.select(CourseModel).where(CourseModel.c.id.in_(recommended_ids))
    ).fetchall()

    # 3. Format the results for JSON
    recommended_courses = [{
        'id': course.id,
        'title': course.title,
        'department': course.department,
        'description': course.description,
        'credits': course.credits
    } for course in courses]
        
    return jsonify({
        "message": f"Successfully retrieved {len(recommended_courses)} recommendations.",
        "courses": recommended_courses
    })

# ----------------------------------------------------------------------
# --- 4. Application Runner ---
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # Runs the Flask server on port 5000 (standard for local backend API)
    app.run(debug=True, port=5000)
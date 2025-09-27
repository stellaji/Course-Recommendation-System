import random
import pandas as pd
from app import app, db, User, Course, Enrollment 

# --- Configuration for Mock Data Volume ---
NUM_USERS = 1000        # 1,000 unique students
NUM_COURSES = 100       # 100 unique courses
NUM_ENROLLMENTS = 25000 # 25,000 historical enrollment records

# --- Helper Data (Customize these lists to be more realistic!) ---
DEPARTMENTS = ['CSE', 'ECE', 'COGS', 'BIPN', 'ECON', 'MATH', 'POLI', 'VIS']
GRADES = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'P', 'F']
SEMESTERS = ['FA22', 'WI23', 'SP23', 'FA23', 'WI24', 'SP24']

def generate_mock_data():
    """Generates synthetic data and loads it into the PostgreSQL database."""
    
    # Use Flask application context to access the database connection
    with app.app_context():
        print("Starting data loading process...")
        
        # Drop and recreate tables to ensure a clean slate
        db.drop_all() 
        db.create_all()
        print("Database tables created successfully.")
        
        # 1. Create Users
        users = []
        for i in range(NUM_USERS):
            major = random.choice(DEPARTMENTS)
            # Use f-string formatting to create distinct usernames
            users.append(User(username=f'student_{i:04d}', major=major))
        db.session.add_all(users)
        db.session.commit()
        print(f"-> Created and committed {NUM_USERS} users.")

        # 2. Create Courses
        courses = []
        for i in range(NUM_COURSES):
            dept = random.choice(DEPARTMENTS)
            title = f'{dept} {random.randint(100, 199):03d} - Subject {i + 1}'
            courses.append(Course(
                title=title, 
                department=dept, 
                description=f'An introduction to {title.split(" ")[-1]} theory.', 
                credits=4
            ))
        db.session.add_all(courses)
        db.session.commit() # Commit to ensure courses have primary keys (IDs)
        print(f"-> Created and committed {NUM_COURSES} courses.")

        # Get IDs after commit for creating Foreign Keys
        all_user_ids = [user.id for user in User.query.all()]
        all_course_ids = [course.id for course in Course.query.all()]

        # 3. Create Enrollments (The bulk of the data)
        enrollments = []
        for _ in range(NUM_ENROLLMENTS):
            user_id = random.choice(all_user_ids)
            course_id = random.choice(all_course_ids)
            semester = random.choice(SEMESTERS)
            grade = random.choice(GRADES)
            
            enrollments.append(Enrollment(
                user_id=user_id,
                course_id=course_id,
                semester=semester,
                grade=grade
            ))
        
        db.session.add_all(enrollments)
        db.session.commit()
        print(f"-> Created and committed {NUM_ENROLLMENTS} enrollment records.")
        print("✅ Mock data loading complete.")

if __name__ == '__main__':
    generate_mock_data()
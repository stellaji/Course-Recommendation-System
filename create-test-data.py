# create_test_data.py

from app import db, app, User, Course, Enrollment # Import models and app from app.py
from random import choice, randint, sample

# A list of user names and courses to create a diverse dataset
TEST_USERS = [
    ('Alice', 'CSE'), ('Bob', 'CSE'), ('Charlie', 'MATH'), 
    ('David', 'ECE'), ('Eve', 'CSE'), ('Frank', 'MATH'), 
    ('Grace', 'POLI'), ('Heidi', 'CSE'), ('Ivan', 'ECON'), 
    ('Judy', 'VIS')
]

# Simple list of departments/titles (use a subset of your existing data)
COURSE_DEPT_TITLES = {
    'CSE': ['Intro to Programming', 'Data Structures', 'Algorithms', 'AI'],
    'MATH': ['Calculus I', 'Linear Algebra', 'Discrete Math'],
    'POLI': ['Intro to IR', 'American Politics', 'Comparative Gov'],
    'ECON': ['Microeconomics', 'Macroeconomics', 'Econometrics'],
    'VIS': ['Digital Art', 'Photography', 'Film History'],
    'ECE': ['Circuits', 'Signal Processing']
}

def create_initial_data():
    """Drops tables, creates tables, and populates with test users and enrollments."""
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        print("Database tables created/recreated.")

        # --- 1. Create Users ---
        user_objects = []
        for name, major in TEST_USERS:
            user = User(username=name, major=major)
            db.session.add(user)
            user_objects.append(user)
        db.session.commit()
        print(f"Created {len(user_objects)} test users.")
        
        # --- 2. Create Courses ---
        course_objects = []
        for dept, titles in COURSE_DEPT_TITLES.items():
            for i, title in enumerate(titles):
                course = Course(
                    title=f'{dept} {i+1}: {title}',
                    department=dept,
                    description=f'An introductory course in {dept}.',
                    credits=4
                )
                db.session.add(course)
                course_objects.append(course)
        db.session.commit()
        print(f"Created {len(course_objects)} test courses.")
        
        # --- 3. Create Enrollments (The vital part for the recommender!) ---
        all_course_ids = [c.id for c in course_objects]
        enrollment_count = 0

        for user in user_objects:
            # Each user enrolls in a random number of courses (3 to 6)
            num_courses = randint(3, 6)
            
            # Select random and unique courses for enrollment
            enrolled_courses = sample(all_course_ids, num_courses)
            
            for course_id in enrolled_courses:
                enrollment = Enrollment(
                    user_id=user.id,
                    course_id=course_id,
                    semester=choice(['Fall 2024', 'Spring 2025']),
                    grade=choice(['A', 'B', 'C', None])
                )
                db.session.add(enrollment)
                enrollment_count += 1
        
        db.session.commit()
        print(f"Created {enrollment_count} total enrollments.")

if __name__ == '__main__':
    create_initial_data()
# create_test_data.py - Realistic Dataset Generator

from app import db, app, User, Course, Enrollment # Import models and app from app.py
from random import choice, randint, sample

# --- 1. Realistic User and Course Data ---

# A list of user names and a wider variety of realistic majors/departments
TEST_USERS = [
    ('Alice', 'CSE'), ('Bob', 'CSE'), ('Charlie', 'MATH'), ('David', 'ECE'), 
    ('Eve', 'CSE'), ('Frank', 'MATH'), ('Grace', 'POLI'), ('Heidi', 'CSE'), 
    ('Ivan', 'ECON'), ('Judy', 'BILD'), ('Kevin', 'PSYC'), ('Laura', 'HIST'),
    ('Mike', 'COGS'), ('Nina', 'PSYC'), ('Oscar', 'POLI'), ('Pam', 'MATH'),
    ('Quinn', 'CSE'), ('Rita', 'ECON'), ('Sam', 'BILD'), ('Tina', 'ECE')
]

# Comprehensive list of departments and course titles (with more courses per dept)
COURSE_DEPT_TITLES = {
    'CSE': [
        'Intro to Programming (CSE 101)', 'Data Structures (CSE 103)', 'Algorithms (CSE 109)', 
        'Web Development (CSE 110)', 'Databases (CSE 111)', 'Computer Architecture (CSE 141)'
    ],
    'MATH': [
        'Calculus I (MATH 10A)', 'Linear Algebra (MATH 20D)', 'Abstract Algebra (MATH 103)', 
        'Probability & Stats (MATH 183)', 'Differential Equations (MATH 120)'
    ],
    'POLI': [
        'Intro to IR', 'American Politics', 'Comparative Government', 
        'Political Theory', 'Public Policy Analysis'
    ],
    'ECON': [
        'Microeconomics (E1A)', 'Macroeconomics (E3A)', 'Econometrics (E120A)', 
        'Game Theory', 'Public Finance'
    ],
    'ECE': [
        'Circuits (E35)', 'Digital Design (E45)', 'Signal Processing (E101)', 
        'Microcontrollers (E111)', 'Electromagnetics (E130)'
    ],
    'BILD': [
        'Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Immunology'
    ],
    'PSYC': [
        'Intro to Psychology (P1)', 'Social Psychology (P104)', 'Developmental Psych (P106)', 
        'Abnormal Psych (P110)', 'Cognitive Neuroscience (P130)'
    ],
    'HIST': [
        'World History (H1)', 'US History (H2)', 'European History (H3)', 
        'History of Science', 'Ancient Greece and Rome'
    ],
    'COGS': [
        'Intro to Cognitive Science (CG1)', 'Human Cognition (CG101)', 
        'AI and Philosophy (CG121)', 'Data Science in CogSci (CG180)', 
        'Cognitive Modeling (CG170)'
    ]
}

# --- 2. Data Generation Logic (Modified) ---

def create_initial_data():
    """Drops tables, creates tables, and populates with a diverse set of users and enrollments."""
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
            for title in titles:
                # Use a slightly more complex title to create unique courses
                course = Course(
                    title=f'{dept}: {title}',
                    department=dept,
                    description=f'An essential course in the field of {dept}.',
                    credits=4
                )
                db.session.add(course)
                course_objects.append(course)
        db.session.commit()
        print(f"Created {len(course_objects)} test courses.")
        
        # --- 3. Create Enrollments (Crucial for Recommender) ---
        all_course_ids = [c.id for c in course_objects]
        enrollment_count = 0

        # Create focused enrollments to ensure majors take classes in their field
        for user in user_objects:
            # 1. Ensure user enrolls in a few courses from their major
            major_courses = [c.id for c in course_objects if c.department == user.major]
            num_major_courses = randint(2, 4)
            
            # Select unique major courses
            enrolled_in_major = sample(major_courses, min(len(major_courses), num_major_courses))

            # 2. Add some random electives from other departments
            num_electives = randint(1, 3)
            # Find non-major courses
            elective_pool = [c_id for c_id in all_course_ids if c_id not in major_courses]
            
            # Select random electives
            enrolled_in_electives = sample(elective_pool, min(len(elective_pool), num_electives))
            
            # Combine unique courses
            enrolled_courses = list(set(enrolled_in_major + enrolled_in_electives))
            
            for course_id in enrolled_courses:
                enrollment = Enrollment(
                    user_id=user.id,
                    course_id=course_id,
                    semester=choice(['Fall 2024', 'Spring 2025', 'Winter 2025']),
                    grade=choice(['A', 'B', 'C', None])
                )
                db.session.add(enrollment)
                enrollment_count += 1
        
        db.session.commit()
        print(f"Created {enrollment_count} total enrollments with major focus.")

if __name__ == '__main__':
    create_initial_data()
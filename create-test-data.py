# create_test_data.py - Data Loader with REAL UCSD Course Titles

from app import db, app, User, Course, Enrollment 
from random import choice, randint, sample

# --- 1. Real Course Data for Key Departments ---
# Data gathered from the UCSD catalog to ensure realistic course titles and numbers

REAL_COURSE_DATA = {
    'CSE': [
        (3, 'Fluency in Information Technology'), (4, 'Introduction to Computer Science'),
        ('6GS', 'Introduction to Computer Science (General Science)'), ('8A', 'Introduction to Computer Science: Java'),
        ('8B', 'Introduction to Computer Science: C++'), (11, 'Introduction to Computer Science and Object-Oriented Programming'),
        (12, 'Basic Data Structures and Object-Oriented Design'), ('15L', 'Software Tools and Techniques Laboratory'),
        (20, 'Discrete Mathematics'), (21, 'Mathematics for Algorithms and Systems'),
        (30, 'Computer Organization and Systems Programming'), (91, 'CSE Honors Seminar'),
        (100, 'Advanced Data Structures'), (101, 'Design and Analysis of Algorithms'),
        (105, 'Theory of Computability'), (107, 'Introduction to Cryptography'),
        (110, 'Software Engineering'), (120, 'Principles of Operating Systems'),
        (130, 'Programming Languages: Principles and Paradigms'), (131, 'Compiler Construction'),
        (140, 'Components and Design Techniques for Digital Systems'), (150, 'Introduction to Artificial Intelligence'),
        (151, 'Artificial Intelligence: Representation and Search'), (167, 'Computer Graphics'),
        (180, 'Database System Principles'), (190, 'Topics in Computer Science and Engineering')
    ],
    'MATH': [
        ('10A', 'Calculus I'), ('10B', 'Calculus II'), ('10C', 'Calculus III'),
        (11, 'Introduction to Linear Algebra'), ('20A', 'Calculus for Science and Engineering I'),
        ('20B', 'Calculus for Science and Engineering II'), (100, 'Abstract Algebra I'),
        (102, 'Applied Linear Algebra'), ('140A', 'Foundations of Real Analysis'),
        ('180A', 'Introduction to Probability'), (190, 'Introduction to Topology')
    ],
    'ECON': [
        (1, 'Principles of Microeconomics'), (2, 'Principles of Macroeconomics'),
        ('100A', 'Microeconomics A'), ('100B', 'Microeconomics B'), ('110A', 'Macroeconomics A'),
        ('120A', 'Econometrics A'), (130, 'Labor Economics'), (140, 'International Trade'),
        (170, 'Game Theory')
    ],
    'POLI': [
        (10, 'Introduction to Political Science: American Politics'), (11, 'Introduction to Political Science: Comparative Politics'),
        (12, 'Introduction to Political Science: International Relations'),
        ('100A', 'The Politics of Globalization'), ('120A', 'Political Science: Data Analytics'),
        ('142A', 'The Politics of the European Union'), ('160A', 'International Political Economy')
    ]
}

# Consolidate all departments we want data for
ALL_DEPARTMENTS = list(REAL_COURSE_DATA.keys()) 
# Add other departments for user diversity, even if their data is generic
ALL_DEPARTMENTS.extend(['BENG', 'BILD', 'CHEM', 'ECE', 'MUS', 'PSYC', 'SOC', 'VIS'])

# --- 2. User Setup (100 users for strong recommendations) ---
TEST_USERS = [(f'User_{i}', choice(ALL_DEPARTMENTS)) for i in range(100)] 

def create_initial_data():
    """Drops tables, creates tables, and populates with a large, realistic dataset."""
    with app.app_context():
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
        
        # --- 2. Create Courses (Using real data where available) ---
        course_objects = []
        course_id_counter = 1
        
        for dept in ALL_DEPARTMENTS:
            if dept in REAL_COURSE_DATA:
                # Use REAL course data
                for number, title in REAL_COURSE_DATA[dept]:
                    # Format title to include department and number, e.g., "CSE 12: Basic Data Structures..."
                    full_title = f'{dept} {number}: {title}'
                    course = Course(
                        id=course_id_counter,
                        title=full_title,
                        department=dept,
                        description=f'Official catalog description for {full_title}.',
                        credits=4
                    )
                    db.session.add(course)
                    course_objects.append(course)
                    course_id_counter += 1
            else:
                # Use generic mock data for non-key departments
                for i in range(1, randint(10, 15)):
                    number = choice([i, i + 100])
                    full_title = f'{dept} {number}: General Topic {i}'
                    course = Course(
                        id=course_id_counter,
                        title=full_title,
                        department=dept,
                        description=f'Mock description for {full_title}.',
                        credits=4
                    )
                    db.session.add(course)
                    course_objects.append(course)
                    course_id_counter += 1
                
        db.session.commit()
        print(f"Created {len(course_objects)} comprehensive test courses.")
        
        # --- 3. Create Enrollments (Essential for the Recommender) ---
        all_course_ids = [c.id for c in course_objects]
        enrollment_count = 0
        
        courses_by_dept = {}
        for c in course_objects:
            courses_by_dept.setdefault(c.department, []).append(c.id)

        for user in user_objects:
            major_dept = user.major
            major_courses_pool = courses_by_dept.get(major_dept, [])
            
            # Ensure user enrolls heavily in their major
            num_major_courses = randint(8, 12)
            # Handle case where dept pool is smaller than requested courses
            if major_courses_pool:
                enrolled_in_major = sample(major_courses_pool, min(len(major_courses_pool), num_major_courses))
            else:
                enrolled_in_major = []

            # Add random electives
            elective_pool = [c_id for c_id in all_course_ids if c_id not in enrolled_in_major]
            num_electives = randint(3, 5)
            enrolled_in_electives = sample(elective_pool, min(len(elective_pool), num_electives))
            
            enrolled_courses = list(set(enrolled_in_major + enrolled_in_electives))
            
            for course_id in enrolled_courses:
                enrollment = Enrollment(
                    user_id=user.id,
                    course_id=course_id,
                    semester=choice(['Fall 2024', 'Spring 2025', 'Winter 2025']),
                    grade=choice(['A', 'B', 'C', 'P'])
                )
                db.session.add(enrollment)
                enrollment_count += 1
        
        db.session.commit()
        print(f"Created {enrollment_count} total comprehensive enrollments.")

if __name__ == '__main__':
    create_initial_data()
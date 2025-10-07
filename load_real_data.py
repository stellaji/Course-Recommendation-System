# load_real_data.py - Loads course data from the course_data.json file

import json
from app import db, app, Course, User, Enrollment
from random import choice, randint, sample

# Configuration
DATA_FILE = 'course_data.json'
NUM_TEST_USERS = 100
# Used for assigning a major to the mock users
MOCK_DEPARTMENTS = ['CSE', 'MATH', 'ECON', 'POLI', 'ECE', 'BILD', 'PSYC', 'HIST'] 

def load_real_courses():
    """Loads courses from a JSON file into the database."""
    try:
        with open(DATA_FILE, 'r') as f:
            course_data_list = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {DATA_FILE} not found. Please create it with real course data.")
        return []
    except json.JSONDecodeError:
        print(f"ERROR: {DATA_FILE} is not valid JSON. Check for missing commas, brackets, or quotes.")
        return []

    course_objects = []
    course_id_counter = 1
    
    for item in course_data_list:
        # Concatenate department and course number to form a complete title for display
        # We ensure department and course_number keys exist to prevent crashes
        dept = item.get('department', 'UNKNOWN')
        num = item.get('course_number', '000')
        title = item.get('title', 'Untitled Course')

        full_title = f"{dept} {num}: {title}"
        
        course = Course(
            id=course_id_counter,
            title=full_title,
            department=dept,
            description=item.get('description', 'No description provided.'),
            credits=item.get('credits', 4)
        )
        db.session.add(course)
        course_objects.append(course)
        course_id_counter += 1
        
    return course_objects

def create_full_data():
    """Drops tables, loads real courses, and creates mock user enrollments."""
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        print("Database tables created/recreated.")

        # 1. Load Real Courses
        course_objects = load_real_courses()
        db.session.commit()
        print(f"Loaded {len(course_objects)} real courses from {DATA_FILE}.")

        if not course_objects:
            print("No courses loaded. Cannot create users or enrollments.")
            return

        # 2. Create Mock Users (still needed for the recommender logic to work)
        user_objects = []
        for i in range(NUM_TEST_USERS):
            major = choice(MOCK_DEPARTMENTS)
            user = User(username=f'Student_{i}', major=major)
            db.session.add(user)
            user_objects.append(user)
        db.session.commit()
        print(f"Created {len(user_objects)} test users.")
        
        # 3. Create Enrollments (The vital part for the recommender!)
        all_course_ids = [c.id for c in course_objects]
        enrollment_count = 0
        
        courses_by_dept = {}
        for c in course_objects:
            courses_by_dept.setdefault(c.department, []).append(c.id)

        for user in user_objects:
            major_dept = user.major
            # Use all courses if the user's major isn't in the loaded data (safer fallback)
            major_courses_pool = courses_by_dept.get(major_dept, all_course_ids)
            
            pool_size = len(major_courses_pool)
            
            # --- ROBUST ENROLLMENT FIX ---
            # Define maximum courses to enroll in (to prevent overly long lists)
            MAX_ENROLLMENT = 6 
            # Define minimum required courses for a recommendation to work well
            MIN_ENROLLMENT = 3 
            
            # Max courses a user takes is the smaller of MAX_ENROLLMENT or the number of available courses
            max_major_enrollment = min(MAX_ENROLLMENT, pool_size)
            
            # Min courses is the smaller of MIN_ENROLLMENT or max_major_enrollment (prevents crash when pool_size < 3)
            min_major_enrollment = min(MIN_ENROLLMENT, max_major_enrollment)
            
            # If the minimum exceeds the maximum (shouldn't happen with the logic above, but safety first)
            if min_major_enrollment > max_major_enrollment:
                 num_major_courses = max_major_enrollment
            else:
                 # Select a random number of courses within the safe, bounded range
                 num_major_courses = choice(range(min_major_enrollment, max_major_enrollment + 1))
            
            # --- END ROBUST ENROLLMENT FIX ---

            # Enroll heavily in their major
            if major_courses_pool and num_major_courses > 0:
                enrolled_in_major = sample(major_courses_pool, num_major_courses)
            else:
                enrolled_in_major = []

            # Add random electives
            elective_pool = [c_id for c_id in all_course_ids if c_id not in enrolled_in_major]
            
            # Choose between 1 and 3 electives, limited by what's available
            MAX_ELECTIVES = 3
            max_electives = min(MAX_ELECTIVES, len(elective_pool))
            
            # Ensure we only call choice on a non-empty range
            if max_electives >= 1:
                num_electives = choice(range(1, max_electives + 1))
                enrolled_in_electives = sample(elective_pool, num_electives)
            else:
                enrolled_in_electives = []
            
            enrolled_courses = list(set(enrolled_in_major + enrolled_in_electives))
            
            for course_id in enrolled_courses:
                enrollment = Enrollment(
                    user_id=user.id,
                    course_id=course_id,
                    semester=choice(['Fall 2024', 'Spring 2025']),
                    grade=choice(['A', 'B', 'C', 'P'])
                )
                db.session.add(enrollment)
                enrollment_count += 1
        
        db.session.commit()
        print(f"Created {enrollment_count} total comprehensive enrollments.")

if __name__ == '__main__':
    create_full_data()
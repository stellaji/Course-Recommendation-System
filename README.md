# Course Recommendation System

Hello! This is a full-stack, data-intensive application designed to generate personalized course recommendations for UCSD students based on their selected major, college, year, and previous course enrollment.

The system utilizes a Collaborative Filtering algorithm implemented in Python to analyze a synthetic dataset of course enrollment and suggest the top 4 courses that align with a user's academic history.

**Key Features**

Full-Stack Architecture: Separated Frontend (React) and Backend (Flask API)

Collaborative Filtering: Uses a data science approach (pandas and Cosine Similarity) to identify possible patterns and suggest courses based on peer enrollment history.

RESTful API: Handles data requests for course catalog retrieval and recommendation generation.

Database Persistence: Course and enrollment data are stored and queried with PostgreSQL, specifically the SQLAlchemy ORM.

Responsive UI: Built with React and styled using React Bootstrap for a clean, professional, and even mobile-friendly user experience.


**Installation and Setup**

This project requires three concurrent processes to run locally: the PostgreSQL database, the Flask backend, and the React frontend.

_Prerequisites_

Python 3.8+ and pip

Node.js and npm

PostgreSQL installed and running on localhost:5432

**Step 1: Database Setup**

Create the Database: Ensure you have a PostgreSQL database named course_recommendations_db.

Note: If you use a different name or credentials, please make sure to update the SQLALCHEMY_DATABASE_URI in app.py.

Install Dependencies: Navigate to the project root in your Terminal and install the included Python dependencies:

pip install -r requirements.txt

(Note: You will need to create a requirements.txt file listing Flask, SQLAlchemy, Pandas, Scikit-learn, etc.)

Initialize Database: Run the Flask application once. 

The if __name__ == '__main__': block, when run with the necessary setup, should create the tables (User, Course, Enrollment) and populate them with mock data.

python app.py 

Wait for tables to be created (you may need to run this twice if data seeding is separate)

**Step 2: Backend Installation**

(Note: The Flask server must be running to serve the course catalog and process recommendations.)

Also make sure you are in the project root directory.

python app.py

Server should be running on http://localhost:5000

**Step 3: Frontend Installation**

The React application serves the UI and communicates with the Flask API.

Install Dependencies: Navigate to the project frontend directory and install Node dependencies:

cd frontend

npm install

Start the Frontend:

npm run dev

Server should be running on http://localhost:5173

**Step 4: Access the Application**

Once both servers are running, open your browser and navigate to:

http://localhost:5173/recommendations

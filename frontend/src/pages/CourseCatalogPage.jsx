import React, { useState, useEffect } from 'react';

const CourseCatalogPage = () => {
  // 1. Define State for courses, loading status, and error
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2. useEffect hook to fetch data when the component mounts
  useEffect(() => {
    // Define the async function inside useEffect
    const fetchCourses = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/courses');
        
        // Check if the response was successful (HTTP status code 200-299)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setCourses(data); // Store the fetched array of courses
        
      } catch (err) {
        console.error("Fetching error:", err);
        setError("Failed to fetch courses. Please ensure the Flask API is running.");
      } finally {
        setIsLoading(false); // Set loading to false regardless of success/fail
      }
    };

    fetchCourses();
  }, []); // The empty array [] ensures this runs only once on mount.

  // 3. Render Logic: Display status messages
  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading course catalog...</div>;
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  }

  // 4. Render Logic: Display the courses
  return (
    <div style={{ padding: '20px' }}>
      <h1>Course Catalog ({courses.length} Courses Found)</h1>
      <p>Data fetched successfully from the Flask API!</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {courses.map((course) => (
          <div key={course.id} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
            <h2>{course.title}</h2>
            <p><strong>Department:</strong> {course.department}</p>
            <p><strong>Credits:</strong> {course.credits}</p>
            {/* Displaying enrollment data from the backend is optional here */}
            {course.enrollment && <p><strong>Enrollment:</strong> {course.enrollment}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CourseCatalogPage;
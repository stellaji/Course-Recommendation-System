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
        setCourses(data); // Store array of courses
        
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
    return <div style={{ padding: '20px' }}>Loading course catalog information...</div>;
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  }

  // 4. Render Logic: Display courses
  return (
    <div style={{ padding: '20px' }}>
      <p className="text-center mb-4" style={{ fontSize: '0.9em', color: '#666' }}>
        Welcome! Please reference the official 
        <a href="https://catalog.ucsd.edu/front/courses.html" target="_blank" rel="noopener noreferrer" style={{marginLeft: '5px', color: '#4A70FF'}}>UCSD Course Catalog</a> 
        &nbsp;for course details.
      </p>
    </div>
  );
};

export default CourseCatalogPage;
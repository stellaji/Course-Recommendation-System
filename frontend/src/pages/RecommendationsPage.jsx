import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; 

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Hardcode the user ID for testing (User ID 1 is guaranteed to have data)
  const USER_ID = 1; 

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // Fetch data from your working Flask endpoint
        const response = await fetch(`http://localhost:5000/api/recommendations/${USER_ID}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.courses && result.courses.length > 0) {
          setRecommendations(result.courses);
        } else {
          // If the backend returns a message about no recommendations
          setError(result.message || "No recommendations found. Data may be too sparse.");
        }
      } catch (err) {
        console.error("Fetching recommendations error:", err);
        setError("Failed to fetch recommendations. Check Flask API status.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [USER_ID]);

  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading personalized recommendations...</div>;
  }
  
  if (error) {
    return <div style={{ padding: '20px', color: 'orange' }}>{error}</div>;
  }
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Personalized Recommendations for User {USER_ID}</h1>
      <p>Based on your enrollment history and similar students:</p>
      
      <div style={{ marginTop: '20px' }}>
        {recommendations.map(course => (
          <div 
            key={course.id} 
            style={{ 
              border: '1px solid #ddd', 
              padding: '15px', 
              marginBottom: '10px', 
              borderRadius: '5px' 
            }}
          >
            <h3 style={{ margin: '0 0 5px 0', color: '#4A70FF' }}>{course.title} ({course.department})</h3>
            <p style={{ margin: '0 0 5px 0' }}>Credits: {course.credits}</p>
            <p style={{ margin: 0, color: '#666', fontSize: '0.9em' }}>{course.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationsPage;
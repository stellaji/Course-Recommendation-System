import React, { useState, useEffect } from 'react';

const DashboardPage = () => {
  // 1. Define State for trends data
  const [trends, setTrends] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2. useEffect hook to fetch data
  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data/trends');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setTrends(data); // Store the fetched array of trends
        
      } catch (err) {
        console.error("Fetching trends error:", err);
        setError("Failed to fetch trends data. Check Flask API status.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrends();
  }, []); // Run only once on mount

  // 3. Render Status Checks
  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading enrollment trends...</div>;
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  }

  // 4. Render the Trends Data (Simple List)
  return (
    <div style={{ padding: '20px' }}>
      <h1>Enrollment Trends Dashboard</h1>
      <p>Data fetched successfully from the Flask API!</p>
      
      <h2>Average Enrollment by Department:</h2>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        {trends && Array.isArray(trends) && trends.map((trend, index) => (
          <li key={index} style={{ padding: '10px', borderBottom: '1px dotted #ccc' }}>
              <strong>{trend.department}:</strong> {Math.round(trend.average_enrollment)} average students
          </li>
        ))}

        {trends && trends.length === 0 && <p>No trend data was returned from the API.</p>}

      </ul>
      
      <p style={{ marginTop: '20px', color: '#666' }}>
        *In the next phase (Phase 4), we will replace this list with charts and data visualizations.
      </p>
    </div>
  );
};

export default DashboardPage;
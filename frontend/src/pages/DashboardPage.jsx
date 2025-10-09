import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap'; 
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';

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
    return (
        <Container fluid className="my-5"> 
            <div style={{ padding: '20px' }}>Loading enrollment trends...</div>
        </Container>
    );
  }

  if (error) {
    return (
        <Container fluid className="my-5">
            <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>
        </Container>
    );
  }
  if (trends.length === 0) {
    return (
      <Container fluid className="my-5">
        <div style={{ padding: '20px' }}>No enrollment trend data found in the database.</div>;
      </Container>
    );
  }

  // 4. Render the Trends Data (Simple List)
  return (
    <Container fluid className="my-5 px-md-5">
      <h1>Enrollment Trends Dashboard</h1>
      <p>Average Enrollment by Department:</p>
      
      {/* 5. Chart Visualization */}
      <div style={{ width: '100%', height: 500 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={trends} // Data is the 'trends' array
            margin={{ top: 5, right: 30, left: 20, bottom: 50 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            
            {/* XAxis uses the 'department' key for labels */}
            <XAxis 
              dataKey="department" 
              angle={-45} // Tilt labels to prevent overlap
              textAnchor="end" 
              interval={0} 
              height={70} 
            /> 
            
            {/* YAxis shows the average enrollment count */}
            <YAxis label={{ value: 'Avg. Enrollment', angle: -90, position: 'insideLeft' }} /> 
            
            <Tooltip 
              formatter={(value) => [`${Math.round(value)} students`, 'Avg. Enrollment']} 
            />
            <Legend verticalAlign="top" height={36} />
            
            {/* Bar uses 'average_enrollment' for bar height */}
            <Bar 
              dataKey="average_enrollment" 
              fill="#4A70FF" // A nice blue color
              name="Avg. Enrollment" 
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p style={{ marginTop: '20px', color: '#666' }}>
        *The visualization shows the average enrollment count for each department.
      </p>
    </Container>
  );
};

export default DashboardPage;
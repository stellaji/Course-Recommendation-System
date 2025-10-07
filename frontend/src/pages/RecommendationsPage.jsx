import React, { useState, useEffect } from 'react';

const RecommendationsPage = () => {
  // 1. STATE FOR USER INPUT
  const [major, setMajor] = useState('CSE'); 
  const [college, setCollege] = useState('Revelle');
  const [year, setYear] = useState('Sophomore');
  const [selectedCourses, setSelectedCourses] = useState([]); // List of course IDs the user has taken
  
  // 2. STATE FOR DATA & STATUS
  const [courseCatalog, setCourseCatalog] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Helper data for dropdowns
  const majors = ['CSE', 'MATH', 'POLI', 'ECON', 'ECE', 'BILD', 'PSYC', 'HIST', 'COGS'];
  const colleges = ['Revelle', 'Marshall', 'Muir', 'Warren', 'Roosevelt', 'Sixth', 'Seventh'];
  const years = ['Freshman', 'Sophomore', 'Junior', 'Senior'];

  // --- EFFECT: Fetch the Course Catalog on load ---
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/courses');
        if (!response.ok) {
          throw new Error('Failed to fetch course catalog.');
        }
        const data = await response.json();
        setCourseCatalog(data);
        setIsLoading(false);
      } catch (err) {
        console.error("Catalog fetch error:", err);
        setError("Failed to load course catalog.");
        setIsLoading(false);
      }
    };
    fetchCatalog();
  }, []);

  // --- HANDLERS ---
  const handleCourseToggle = (courseId) => {
    setSelectedCourses(prev => 
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId) // Remove
        : [...prev, courseId] // Add
    );
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setRecommendations(null); // Clear previous results
    setError(null);
    
    // 3. API Call: POST user data to a new endpoint
    try {
      const response = await fetch('http://localhost:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          major: major,
          college: college,
          year: year,
          taken_course_ids: selectedCourses,
          // Note: The backend will only use 'taken_course_ids' for the recommender logic
        }),
      });

      const result = await response.json();
      
      if (!response.ok || result.courses.length === 0) {
        throw new Error(result.message || "Could not generate recommendations.");
      }
      
      setRecommendations(result.courses);
    } catch (err) {
      console.error("Recommendation submission error:", err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- RENDER STATUS CHECKS ---
  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading course catalog...</div>;
  }
  
  const filteredCatalog = courseCatalog.filter(
    course => course.title.toLowerCase() // Filter the catalog for easier selection
  );

  // --- RENDER COMPONENT ---
  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1>Wondering what classes to take next?</h1>
      <p>Select the courses you have already taken and provide your details to receive 4 suggested courses for the next quarter.</p>

      {/* 4. RECOMMENDATION RESULTS DISPLAY */}
      {recommendations && (
        <div style={{ border: '2px solid #4A70FF', padding: '20px', margin: '20px 0', borderRadius: '8px', background: '#F5F8FF' }}>
          <h2 style={{ color: '#4A70FF' }}>Your Top 4 Recommended Courses:</h2>
          {recommendations.map(course => (
            <div key={course.id} style={{ marginBottom: '10px', borderBottom: '1px dotted #ccc' }}>
              <h3 style={{ margin: '5px 0', fontSize: '1.1em' }}>{course.title} ({course.department})</h3>
            </div>
          ))}
          <button onClick={() => setRecommendations(null)} style={{ marginTop: '15px' }}>
            Modify Input
          </button>
        </div>
      )}
      
      {/* 5. INPUT FORM (Hidden when recommendations are shown) */}
      {!recommendations && (
        <form onSubmit={handleSubmit}>
          {/* USER INFO DROPDOWNS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '20px' }}>
            <label>Major:
              <select value={major} onChange={e => setMajor(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }}>
                {majors.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </label>
            <label>College:
              <select value={college} onChange={e => setCollege(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }}>
                {colleges.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </label>
            <label>Year:
              <select value={year} onChange={e => setYear(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }}>
                {years.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </label>
          </div>

          {/* COURSE SELECTION */}
          <h2>Courses Already Taken ({selectedCourses.length} Selected)</h2>
          <div style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
            {filteredCatalog.map(course => (
              <div 
                key={course.id} 
                style={{ 
                  padding: '5px', 
                  borderBottom: '1px dotted #eee', 
                  cursor: 'pointer',
                  background: selectedCourses.includes(course.id) ? '#e6f0ff' : 'transparent' 
                }}
                onClick={() => handleCourseToggle(course.id)}
              >
                <input 
                  type="checkbox" 
                  checked={selectedCourses.includes(course.id)} 
                  readOnly 
                  style={{ marginRight: '10px' }} 
                />
                {course.title} ({course.department})
              </div>
            ))}
          </div>

          {/* SUBMIT BUTTON */}
          <button 
            type="submit" 
            disabled={isSubmitting || selectedCourses.length < 2} // Require at least 2 courses to submit
            style={{ 
              marginTop: '20px', 
              padding: '10px 20px', 
              fontSize: '1em', 
              cursor: isSubmitting || selectedCourses.length < 2 ? 'not-allowed' : 'pointer'
            }}
          >
            {isSubmitting ? 'Generating...' : `Get 4 Course Recommendations`}
          </button>
          
          {error && <p style={{ color: 'red', marginTop: '10px' }}>Error: {error}</p>}
        </form>
      )}
    </div>
  );
};

export default RecommendationsPage;
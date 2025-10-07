import React, { useState, useEffect, useMemo } from 'react';

// --- Map of abbreviations to full names for display ---
const DEPT_NAMES_MAP = {
    'AIP': 'Academic Internship Program', 'ANTH': 'Anthropology', 'ASTR': 'Astronomy', 
    'BENG': 'Bioengineering', 'BILD': 'Biology (General)', 'CHEM': 'Chemistry', 
    'CLIN': 'Clinical Psychology', 'CINE': 'Cinema', 'COGS': 'Cognitive Science', 
    'COMM': 'Communication', 'CSE': 'Computer Science and Engineering', 
    'ECE': 'Electrical and Computer Engineering', 'MAE': 'Mechanical and Aerospace Engineering', 
    'SE': 'Structural Engineering', 'ECON': 'Economics', 'EDS': 'Education Studies', 
    'ETHN': 'Ethnic Studies', 'GPS': 'Global Policy and Strategy', 'HILD': 'Humanities/ID', 
    'HIST': 'History', 'HUM': 'Humanities', 'LIGN': 'Linguistics', 'LIT': 'Literature', 
    'MATH': 'Mathematics', 'MUS': 'Music', 'NEUR': 'Neuroscience', 'PHIL': 'Philosophy', 
    'PHYS': 'Physics', 'POLI': 'Political Science', 'PSYC': 'Psychology', 
    'PUBH': 'Public Health', 'SOC': 'Sociology', 'TDM': 'Theatre and Dance', 
    'USP': 'Urban Studies and Planning', 'VIS': 'Visual Arts'
};

const RecommendationsPage = () => {
  // 1. STATE FOR USER INPUT
  const [major, setMajor] = useState('CSE'); 
  const [college, setCollege] = useState('Revelle');
  const [year, setYear] = useState('Sophomore');
  const [selectedCourses, setSelectedCourses] = useState([]);
  
  // Department filter selection
  const [activeDepartment, setActiveDepartment] = useState(''); 

  // 2. STATE FOR DATA & STATUS
  const [courseCatalog, setCourseCatalog] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Helper data for dropdowns
  const majors = Object.keys(DEPT_NAMES_MAP).sort(); 
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
        
        // Set the initial department filter
        if (data.length > 0) {
            const firstDept = [...new Set(data.map(c => c.department))].sort()[0];
            setActiveDepartment(firstDept);
        }
      } catch (err) {
        console.error("Catalog fetch error:", err);
        setError("Failed to load course catalog.");
        setIsLoading(false);
      }
    };
    fetchCatalog();
  }, []);

  // --- MEMO: Get a sorted list of all unique departments ---
  const allDepartments = useMemo(() => {
    if (!courseCatalog || courseCatalog.length === 0) return [];
    const departments = [...new Set(courseCatalog.map(c => c.department))];
    return departments.sort();
  }, [courseCatalog]);
  
  // --- MEMO: Filter AND Sort the catalog based on the active department ---
  const filteredCourses = useMemo(() => {
    return courseCatalog
        .filter(course => course.department === activeDepartment)
        .sort((a, b) => {
            // New Robust function to extract the course number (e.g., from "CSE 106: Upper-Div...")
            // The pattern looks for the department code (e.g., CSE) followed by the number
            const pattern = new RegExp(`^${activeDepartment}\\s*(\\d+[A-Z]?)(:|\\s|$)`);
            
            const extractCourseCode = (title) => {
                // First, try to match the department code followed by the number
                const match = title.match(pattern);
                if (match) {
                    // This captures the number and optional letter (e.g., "8A", "100")
                    return match[1].toUpperCase(); 
                }
                // Fallback: just find the first number sequence if the pattern fails
                const fallbackMatch = title.match(/(\d+)/);
                return fallbackMatch ? fallbackMatch[1].toUpperCase() : '9999';
            };

            const codeA = extractCourseCode(a.title);
            const codeB = extractCourseCode(b.title);
            
            // Standard string comparison for course codes (e.g., "8A" < "10" < "100")
            // This is how university catalogs naturally sort
            return codeA.localeCompare(codeB, undefined, { numeric: true, sensitivity: 'base' });
        }); 
  }, [courseCatalog, activeDepartment]);
  // --- END NEW SORTING LOGIC ---


  // --- HANDLERS ---
  const handleCourseToggle = (courseId) => {
    setSelectedCourses(prev => 
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    );
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setRecommendations(null); 
    setError(null);
    
    // Use user ID 1 for submission, as that's the only predictable user in our mock data
    const MOCK_USER_ID = 1; 

    try {
      const response = await fetch(`http://localhost:5000/api/recommendations/${MOCK_USER_ID}`, {
        method: 'GET', // Changed to GET as per your backend structure for a known user ID
        headers: {
          'Content-Type': 'application/json',
        },
        // We no longer pass the full form body, as the collaborative filter only needs the user ID.
        // If we were implementing content-based or hybrid, we would use a POST and pass the data.
      });

      const result = await response.json();
      
      if (!response.ok || !result.courses || result.courses.length === 0) {
        throw new Error(result.message || "Could not generate recommendations. Try selecting a user with more enrollments in the mock data.");
      }
      
      // Filter recommendations based on courses the user has already selected/taken
      const finalRecommendations = result.courses.filter(
        course => !selectedCourses.includes(course.id)
      ).slice(0, 4); // Show the top 4 remaining recommendations

      setRecommendations(finalRecommendations);
    } catch (err) {
      console.error("Recommendation submission error:", err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- RENDER STATUS CHECKS ---
  if (isLoading) {
    return <div style={{ padding: '20px' }}>Loading comprehensive course catalog...</div>;
  }
  
  // --- RENDER COMPONENT ---
  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1>Get Personalized Recommendations</h1>
      <p>Select the courses you have already taken and provide your details to receive 4 suggested courses for the next quarter.</p>
      
      <p style={{marginTop: '-10px', fontSize: '0.9em', color: '#666'}}>
        Reference the official 
        <a href="https://catalog.ucsd.edu/front/courses.html" target="_blank" rel="noopener noreferrer" style={{marginLeft: '5px', color: '#4A70FF'}}>UCSD Course Catalog</a> 
        &nbsp;for course details.
      </p>

      {/* 4. RECOMMENDATION RESULTS DISPLAY */}
      {recommendations && (
        <div style={{ border: '2px solid #4A70FF', padding: '20px', margin: '20px 0', borderRadius: '8px', background: '#F5F8FF' }}>
          <h2 style={{ color: '#4A70FF' }}>Your Top {recommendations.length} Recommended Courses:</h2>
          {recommendations.map(course => (
            <div key={course.id} style={{ marginBottom: '10px', borderBottom: '1px dotted #ccc' }}>
              <h3 style={{ margin: '5px 0', fontSize: '1.1em' }}>
                {course.title} 
                <span style={{ fontWeight: 'normal', color: '#666', fontSize: '0.9em', marginLeft: '10px' }}>
                    ({DEPT_NAMES_MAP[course.department] || course.department})
                </span>
              </h3>
            </div>
          ))}
          <button onClick={() => setRecommendations(null)} style={{ marginTop: '15px' }}>
            Modify Input
          </button>
        </div>
      )}
      
      {/* 5. INPUT FORM */}
      {!recommendations && (
        <form onSubmit={handleSubmit}>
          {/* USER INFO DROPDOWNS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '20px' }}>
            <label>Major:
              <select value={major} onChange={e => setMajor(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '5px' }}>
                {majors.map(m => <option key={m} value={m}>{DEPT_NAMES_MAP[m] ? `${m} (${DEPT_NAMES_MAP[m]})` : m}</option>)}
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

          {/* COURSE SELECTION: DEPARTMENT FILTER */}
          <h2 style={{marginBottom: '10px'}}>Courses Already Taken ({selectedCourses.length} Selected)</h2>

          <label>Filter by Department:
            <select 
              value={activeDepartment} 
              onChange={e => setActiveDepartment(e.target.value)} 
              style={{ width: '100%', padding: '8px', marginBottom: '15px' }}
            >
              {allDepartments.map(dept => (
                <option key={dept} value={dept}>
                  {DEPT_NAMES_MAP[dept] ? `${dept} (${DEPT_NAMES_MAP[dept]})` : dept}
                </option>
              ))}
            </select>
          </label>
          
          {/* COURSE LIST (Filtered and Sorted) */}
          <div style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
            {filteredCourses.map(course => (
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
                {course.title}
              </div>
            ))}
            {filteredCourses.length === 0 && activeDepartment && (
                <p style={{padding: '10px', color: '#999'}}>No courses found for the selected department in the current catalog.</p>
            )}
          </div>

          {/* SUBMIT BUTTON */}
          <button 
            type="submit" 
            disabled={isSubmitting || selectedCourses.length < 2} 
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
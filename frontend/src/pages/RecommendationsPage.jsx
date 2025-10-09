import React, { useState, useEffect, useMemo } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';

const BACKEND_URL = "http://localhost:5000"

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
    
    if (selectedCourses.length < 2) {
      setError("Please select at least two courses taken to generate recommendations.");
      setIsSubmitting(false);
      return;
    }

    try {
      // --- CRITICAL CHANGE: Use POST method and the /api/recommend endpoint ---
      const response = await fetch(`${BACKEND_URL}/api/recommend`, {
        method: 'POST', // <-- Must be POST
        headers: {
          'Content-Type': 'application/json',
        },
        // --- Send the list of selected course IDs in the body ---
        body: JSON.stringify({ 
            taken_course_ids: selectedCourses // <-- Key required by app.py
        }), 
      });

      const result = await response.json();
      
      if (!response.ok) {
        // If the backend returns a 400 or other non-OK status
        throw new Error(result.message || "Recommendation fetch failed due to a server error.");
      }
      
      // If result.courses is empty (e.g., if the algorithm finds no matches)
      if (!result.courses || result.courses.length === 0) {
        throw new Error(result.message || "No specific recommendations found. Try selecting different courses.");
      }
      
      // No need to filter by selected courses here, as the backend algorithm should handle it.
      // But we will take the top 4 if the backend sends more.
      setRecommendations(result.courses.slice(0, 4));

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
    <Container fluid className="my-5" style={{ maxWidth: '1000px' }}>
      <h1 className="text-center mb-3">Get Personalized Recommendations</h1>
      <p className="text-center lead text-muted">
        Select the courses you have already taken and provide your details to receive 4 suggested courses for the next quarter.
      </p>

      {/* 2. RECOMMENDATION RESULTS DISPLAY */}
      {recommendations && (
        <div className="p-4 mb-4 border rounded shadow-sm" style={{ borderColor: '#4A70FF', background: '#f8f9fa' }}>
          <h2 className="text-success mb-3" style={{ fontSize: '1.5em' }}>
            ✅ Your Top {recommendations.length} Recommended Courses:
          </h2>
          <ul className="list-unstyled">
            {recommendations.map(course => (
              <li key={course.id} className="mb-2 pb-2" style={{ borderBottom: '1px dotted #ccc' }}>
                <h3 style={{ margin: '5px 0', fontSize: '1.1em' }}>
                    <strong>{course.title}</strong>
                    <span className="text-muted" style={{ fontWeight: 'normal', fontSize: '0.9em', marginLeft: '10px' }}>
                        ({DEPT_NAMES_MAP[course.department] || course.department})
                    </span>
                </h3>
                <p className="text-muted small mb-0">{course.description.substring(0, 150)}...</p>
              </li>
            ))}
          </ul>
          {/* Use the Bootstrap Button component */}
          <Button variant="outline-secondary" size="sm" onClick={() => setRecommendations(null)} className="mt-3">
            Modify Input
          </Button>
        </div>
      )}
      
      {/* 3. INPUT FORM */}
      {!recommendations && (
        // Replace <form> with the Form component and add styling classes
        <Form onSubmit={handleSubmit} className="p-4 border rounded shadow">
          
          {/* USER INFO DROPDOWNS: Use Row and Col for a responsive grid */}
          <Row className="mb-4">
            {/* Major */}
            <Col md={4}>
              <Form.Group controlId="formMajor">
                <Form.Label>Major:</Form.Label>
                <Form.Select value={major} onChange={e => setMajor(e.target.value)}>
                  {majors.map(m => <option key={m} value={m}>{DEPT_NAMES_MAP[m] ? `${m} (${DEPT_NAMES_MAP[m]})` : m}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
            
            {/* College */}
            <Col md={4}>
              <Form.Group controlId="formCollege">
                <Form.Label>College:</Form.Label>
                <Form.Select value={college} onChange={e => setCollege(e.target.value)}>
                  {colleges.map(c => <option key={c} value={c}>{c}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
            
            {/* Year */}
            <Col md={4}>
              <Form.Group controlId="formYear">
                <Form.Label>Year:</Form.Label>
                <Form.Select value={year} onChange={e => setYear(e.target.value)}>
                  {years.map(y => <option key={y} value={y}>{y}</option>)}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          {/* COURSE SELECTION: DEPARTMENT FILTER */}
          <h2 className="mb-3" style={{ fontSize: '1.5em' }}>
            Courses Already Taken ({selectedCourses.length} Selected)
          </h2>

          <Form.Group controlId="formDepartmentFilter" className="mb-3">
            <Form.Label>Filter by Department:</Form.Label>
            <Form.Select 
              value={activeDepartment} 
              onChange={e => setActiveDepartment(e.target.value)} 
            >
              {allDepartments.map(dept => (
                <option key={dept} value={dept}>
                  {DEPT_NAMES_MAP[dept] ? `${dept} (${DEPT_NAMES_MAP[dept]})` : dept}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
          
          {/* COURSE LIST (Filtered and Sorted) */}
          {/* Use Bootstrap classes for the scrollable list */}
          <div className="list-group" style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ccc', borderRadius: '5px' }}>
            {filteredCourses.map(course => (
              <div 
                key={course.id} 
                // Use list-group-item and active class for styling
                className={`list-group-item list-group-item-action ${selectedCourses.includes(course.id) ? 'active' : ''}`}
                onClick={() => handleCourseToggle(course.id)}
                style={{ cursor: 'pointer' }}
              >
                {/* Use Form.Check for a clean look inside the list item */}
                <Form.Check 
                    type="checkbox" 
                    label={course.title}
                    checked={selectedCourses.includes(course.id)} 
                    readOnly 
                    // Prevent the click on the checkbox from double-triggering the toggle
                    style={{pointerEvents: 'none'}}
                />
              </div>
            ))}
            {filteredCourses.length === 0 && activeDepartment && (
                <p className="text-center text-muted p-3">No courses found for the selected department in the current catalog.</p>
            )}
          </div>

          {/* SUBMIT BUTTON */}
          <Button 
            type="submit" 
            variant="primary" // Primary color button
            size="lg" // Large button
            disabled={isSubmitting || selectedCourses.length < 2} 
            className="w-100 mt-4" // Full width
          >
            {isSubmitting ? 'Generating...' : `Get 4 Course Recommendations`}
          </Button>
          
          {error && <p className="text-danger mt-3">Error: {error}</p>}
        </Form>
      )}
    </Container>
  );
};

export default RecommendationsPage;
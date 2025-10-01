import { Link } from 'react-router-dom';

const Navbar = () => {
  const linkStyle = { 
    color: 'white', 
    marginRight: '25px', 
    textDecoration: 'none',
    fontWeight: 'bold'
  };

  return (
    <nav style={{ padding: '15px 30px', backgroundColor: '#282c34', display: 'flex' }}>
      <Link to="/" style={linkStyle}>Home</Link>
      <Link to="/catalog" style={linkStyle}>Course Catalog</Link>
      <Link to="/dashboard" style={linkStyle}>Trends Dashboard</Link>
      <Link to="/recommendations">My Recommendations</Link> 
    </nav>
  );
};
export default Navbar;
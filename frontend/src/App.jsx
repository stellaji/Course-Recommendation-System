import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage.jsx';
import CatalogPage from './pages/CourseCatalogPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import Navbar from './components/Navbar.jsx'; // 
import RecommendationsPage from './pages/RecommendationsPage.jsx'; 
import './App.css'; // Assuming CSS

function App() {
  return (
    <BrowserRouter>
      {/* Navbar will appear on all pages */}
      <Navbar /> 
      
      <div className="container-fluid p-0">
        <Routes>
          {/* Main application routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/catalog" element={<CatalogPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} /> 
          <Route path="*" element={<h1>404: Page Not Found</h1>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

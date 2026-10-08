import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Camera, Search, Activity, Camera as CameraIcon } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Cameras from './pages/Cameras';
import Events from './pages/Events';

import './index.css';

const Sidebar = () => {
  const location = useLocation();
  
  const links = [
    { name: 'Ask Cameras', path: '/', icon: <Search size={20} /> },
    { name: 'Cameras', path: '/cameras', icon: <Camera size={20} /> },
    { name: 'Events', path: '/events', icon: <Activity size={20} /> },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        Multi-camera-intelligence
        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 'normal', marginTop: '4px'}}>
          "Ask your cameras what happened."
        </div>
      </div>
      <div className="nav-links">
        {links.map((link) => (
          <Link 
            to={link.path} 
            key={link.path}
            className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
          >
            {link.icon}
            {link.name}
          </Link>
        ))}
      </div>
      <div className="system-status">
        <div className="status-item">
          <div className="status-dot"></div>
          Cameras Online
        </div>
        <div className="status-item">
          <div className="status-dot"></div>
          Index Ready
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cameras" element={<Cameras />} />
            <Route path="/events" element={<Events />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;

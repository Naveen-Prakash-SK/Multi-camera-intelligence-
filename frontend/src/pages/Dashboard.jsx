import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, CheckCircle, Video, Image as ImageIcon } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

const Dashboard = () => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [response, setResponse] = useState(null);
  const [clarification, setClarification] = useState(null);
  const [cameras, setCameras] = useState([]);

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      const res = await axios.get(`${API_URL}/cameras`);
      setCameras(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    
    setIsSearching(true);
    setResponse(null);
    setClarification(null);

    // Simple clarify-once check logic in frontend for hackathon demo
    const unknownTerms = ['main gate', 'lobby', 'parking'];
    let needsClarification = false;
    let termToClarify = '';

    for (let term of unknownTerms) {
      if (query.toLowerCase().includes(term)) {
        try {
          const memRes = await axios.get(`${API_URL}/memory?key=${encodeURIComponent(term)}`);
          if (!memRes.data.value) {
            needsClarification = true;
            termToClarify = term;
            break;
          }
        } catch (e) {}
      }
    }

    if (needsClarification) {
      setIsSearching(false);
      setClarification(termToClarify);
      return;
    }

    try {
      const res = await axios.post(`${API_URL}/search`, { query });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      setResponse({ error: "BACKEND CONNECTION ERROR", results: [] });
    }
    
    setIsSearching(false);
  };

  const handleClarify = async (cameraId) => {
    try {
      await axios.post(`${API_URL}/memory`, { key: clarification, value: cameraId });
      setClarification(null);
      // Re-run search
      const res = await axios.post(`${API_URL}/search`, { query });
      setResponse(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <h1 className="page-header">CCTV Intelligence</h1>
      
      <div className="search-container">
        <h2 style={{marginTop: 0, fontSize: '1.2rem', marginBottom: '15px'}}>Ask your cameras</h2>
        <form onSubmit={handleSearch} className="search-input-wrapper">
          <input 
            type="text" 
            className="search-input" 
            placeholder="e.g. Did a red car enter the main gate?" 
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button type="submit" className="btn" disabled={isSearching}>
            <Search size={18} />
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {clarification && (
        <div className="result-card" style={{borderColor: 'var(--accent)'}}>
          <h3 style={{marginTop: 0, color: 'var(--accent)'}}>Clarification Needed</h3>
          <p>Which camera represents <strong>"{clarification}"</strong>?</p>
          <div style={{display: 'flex', gap: '10px', marginTop: '15px'}}>
            {cameras.map(c => (
              <button 
                key={c.camera_id} 
                className="btn btn-secondary"
                onClick={() => handleClarify(c.camera_id)}
              >
                {c.camera_name}
              </button>
            ))}
          </div>
        </div>
      )}

      {response && !clarification && (
        <div className="result-card">
          {response.error ? (
            <div className="result-header">
              <span style={{color: 'var(--danger)'}}>{response.error}</span>
            </div>
          ) : (
            <>
              <div className="result-header">
                {response.results && response.results.length > 0 && response.results[0].verified ? (
                  <span style={{color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <CheckCircle size={24} /> MATCH FOUND
                  </span>
                ) : (
                  <span style={{color: 'var(--danger)'}}>NO VERIFIED MATCH FOUND</span>
                )}
              </div>
              
              <p style={{marginBottom: '25px', fontSize: '1.1rem'}}>{response.answer}</p>
            </>
          )}
          
          {response.results && response.results.length > 0 && response.results[0].verified && (
            <div>
              <div className="result-meta">
                <div className="meta-item">
                  <span className="meta-label">Camera</span>
                  <span className="meta-value">{response.results[0].camera_name}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Timestamp</span>
                  <span className="meta-value">{response.results[0].timestamp}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Event</span>
                  <span className="meta-value">{response.results[0].description}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Confidence</span>
                  <span className="meta-value">{(response.results[0].score * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="evidence-box">
                <h4 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <ImageIcon size={18} /> Evidence Frame
                </h4>
                {response.results[0].frame_url ? (
                   <img 
                     src={`http://localhost:8000${response.results[0].frame_url}`} 
                     alt="Evidence" 
                     className="evidence-img"
                     onError={(e) => { 
                       e.target.style.display = 'none'; 
                       if (e.target.nextSibling) e.target.nextSibling.style.display = 'block'; 
                     }}
                   />
                ) : null}
                <div style={{display: response.results[0].frame_url ? 'none' : 'block', color: 'var(--danger)', padding: '15px 0'}}>
                  EVIDENCE UNAVAILABLE
                </div>
                
                {response.results[0].clip_url && (
                  <div style={{marginTop: '20px'}}>
                    <h4 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                      <Video size={18} /> Evidence Clip
                    </h4>
                    <video 
                      src={`http://localhost:8000${response.results[0].clip_url}`} 
                      controls 
                      className="evidence-img"
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;

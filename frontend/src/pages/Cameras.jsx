import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Camera as CameraIcon } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

const Cameras = () => {
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

  return (
    <div>
      <h1 className="page-header">Cameras</h1>
      <div className="card-grid">
        {cameras.map(c => (
          <div className="card" key={c.camera_id}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px'}}>
              <CameraIcon size={24} color="var(--accent)" />
              <h3 className="card-title" style={{margin: 0}}>{c.camera_name}</h3>
            </div>
            <p className="card-subtitle">{c.camera_id}</p>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px'}}>
              <span style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{c.location}</span>
              <span className="badge">{c.status}</span>
            </div>
          </div>
        ))}
        {cameras.length === 0 && (
          <p>No cameras registered yet.</p>
        )}
      </div>
    </div>
  );
};

export default Cameras;

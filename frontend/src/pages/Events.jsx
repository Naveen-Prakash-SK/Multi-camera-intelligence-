import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

const Events = () => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const res = await axios.get(`${API_URL}/events`);
      setEvents(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <h1 className="page-header">Events</h1>
      
      <div style={{display: 'flex', gap: '30px'}}>
        <div style={{flex: 1, backgroundColor: 'var(--bg-panel)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden'}}>
          <table className="table">
            <thead>
              <tr>
                <th>Camera</th>
                <th>Time</th>
                <th>Event</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {events.map(e => (
                <tr key={e.id}>
                  <td>{e.camera_name}</td>
                  <td>{e.timestamp}</td>
                  <td>{e.description}</td>
                  <td>
                    <button 
                      className="btn btn-secondary" 
                      style={{padding: '6px 12px', fontSize: '0.85rem'}}
                      onClick={() => setSelectedEvent(e)}
                    >
                      <Play size={14} /> View
                    </button>
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan="4" style={{textAlign: 'center', padding: '20px'}}>No events indexed yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {selectedEvent && (
          <div style={{width: '350px'}}>
            <div className="card">
              <h3 className="card-title">Evidence</h3>
              <p className="card-subtitle">{selectedEvent.timestamp} • {selectedEvent.camera_name}</p>
              
              <div style={{marginTop: '20px'}}>
                {selectedEvent.frame_url ? (
                  <img 
                    src={`http://localhost:8000${selectedEvent.frame_url}`} 
                    alt="Evidence" 
                    className="evidence-img"
                  />
                ) : (
                  <div style={{padding: '40px', textAlign: 'center', backgroundColor: 'var(--bg-dark)', borderRadius: '4px'}}>
                    No visual evidence
                  </div>
                )}
              </div>
              
              <div style={{marginTop: '20px'}}>
                <strong>Description:</strong>
                <p style={{marginTop: '5px', color: 'var(--text-muted)'}}>{selectedEvent.description}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Events;

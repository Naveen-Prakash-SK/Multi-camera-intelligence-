"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera } from "@/types";
import { Camera as CameraIcon, Plus, Trash2, Edit2, Play, Square, AlertTriangle, Loader2 } from "lucide-react";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ id: "", name: "", location: "", description: "", source_type: "file", stream_url: "" });
  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const fetchCameras = async () => {
    setLoading(true);
    try {
      const data = await api.getCameras();
      setCameras(data);
    } catch (err: any) {
      setError("Failed to load cameras");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCameras();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      if (isEditing) {
        await api.updateCamera(formData.id, formData);
      } else {
        await api.createCamera(formData);
      }
      await fetchCameras();
      setShowForm(false);
      setFormData({ id: "", name: "", location: "", description: "", source_type: "file", stream_url: "" });
    } catch (err: any) {
      setError(err.message || "Failed to save camera");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this camera?")) return;
    try {
      await api.deleteCamera(id);
      setCameras(cameras.filter(c => c.id !== id));
    } catch (err: any) {
      setError("Failed to delete camera");
    }
  };

  const toggleStatus = async (cam: Camera) => {
    try {
      if (cam.status === 'ONLINE') {
        await api.stopCamera(cam.id);
        setCameras(cameras.map(c => c.id === cam.id ? { ...c, status: 'OFFLINE' } : c));
      } else {
        await api.startCamera(cam.id);
        setCameras(cameras.map(c => c.id === cam.id ? { ...c, status: 'ONLINE' } : c));
      }
    } catch (err: any) {
      setError("Failed to change camera status");
    }
  };

  const openEdit = (cam: Camera) => {
    setFormData({ id: cam.id, name: cam.name, location: cam.location || "", description: cam.description || "", source_type: cam.source_type || "file", stream_url: cam.stream_url || "" });
    setIsEditing(true);
    setShowForm(true);
  };

  const openCreate = () => {
    setFormData({ id: "", name: "", location: "", description: "", source_type: "file", stream_url: "" });
    setIsEditing(false);
    setShowForm(true);
  };

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8 animate-in fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
            <CameraIcon className="w-8 h-8 mr-3 text-blue-500" />
            Camera Management
          </h1>
          <p className="text-neutral-400">Manage logical camera sources for recorded footage ingestion.</p>
        </div>
        <button 
          onClick={openCreate}
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-all flex items-center shadow-lg shadow-blue-500/20"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Camera
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start text-red-400">
          <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {showForm && (
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 shadow-xl mb-8">
          <h2 className="text-lg font-bold text-white mb-4">{isEditing ? "Edit Camera" : "Register New Camera"}</h2>
          <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-1">Camera Name</label>
                <input 
                  required
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                  placeholder="e.g. CAM-01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-1">Location</label>
                <input 
                  required
                  type="text" 
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                  placeholder="e.g. Main Gate"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-1">Source Type</label>
                <select 
                  value={formData.source_type}
                  onChange={(e) => setFormData({...formData, source_type: e.target.value})}
                  className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="file">Recorded Source</option>
                  <option value="live">Live API Stream</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-400 mb-1">Stream URL (Optional)</label>
                <input 
                  type="text" 
                  value={formData.stream_url}
                  onChange={(e) => setFormData({...formData, stream_url: e.target.value})}
                  className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none disabled:opacity-50"
                  placeholder="e.g. http://127.0.0.1:8001/health"
                  disabled={formData.source_type !== 'live'}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-1">Description (Optional)</label>
              <textarea 
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none h-20 resize-none"
              />
            </div>
            <div className="flex space-x-3 pt-2">
              <button 
                type="button" 
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                disabled={submitting}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium text-sm flex items-center"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {isEditing ? "Save Changes" : "Register Camera"}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1,2,3].map(i => <div key={i} className="h-48 bg-neutral-900 rounded-xl animate-pulse"></div>)}
        </div>
      ) : cameras.length > 0 ? (
        <div className="space-y-12">
          {/* LIVE CAMERAS */}
          {cameras.some(c => c.source_type === 'live') && (
            <div>
              <div className="mb-4 flex items-center">
                <div className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse"></div>
                <h2 className="text-xl font-bold text-white">Live API Cameras</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cameras.filter(c => c.source_type === 'live').map(cam => (
                  <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 shadow-lg flex flex-col hover:border-neutral-700 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-white text-lg flex items-center">
                          {cam.name}
                          <span className="ml-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-red-500/10 text-red-400 border border-red-500/20">
                            Live Source
                          </span>
                        </h3>
                        <p className="text-sm text-neutral-400 mt-1">{cam.location}</p>
                      </div>
                      <div className={`px-2 py-1 rounded border text-[10px] font-bold tracking-widest uppercase ${cam.status === 'ONLINE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-neutral-800 text-neutral-500 border-neutral-700'}`}>
                        {cam.status === 'ONLINE' ? 'READY' : 'OFFLINE'}
                      </div>
                    </div>
                    
                    <p className="text-sm text-neutral-500 mb-6 flex-1">{cam.description || "No description provided."}</p>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-neutral-800">
                      <button 
                        onClick={() => toggleStatus(cam)}
                        className={`flex items-center text-sm font-medium transition-colors ${cam.status === 'ONLINE' ? 'text-red-400 hover:text-red-300' : 'text-emerald-400 hover:text-emerald-300'}`}
                      >
                        {cam.status === 'ONLINE' ? (
                          <><Square className="w-4 h-4 mr-1.5" /> Stop</>
                        ) : (
                          <><Play className="w-4 h-4 mr-1.5" /> Start</>
                        )}
                      </button>
                      
                      <div className="flex space-x-2">
                        <button onClick={() => openEdit(cam)} className="p-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-300 transition-colors">
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleDelete(cam.id)} className="p-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-red-400 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* RECORDED CAMERAS */}
          {cameras.some(c => c.source_type !== 'live') && (
            <div>
              <div className="mb-4">
                <h2 className="text-xl font-bold text-white">Recorded Sources</h2>
                <p className="text-sm text-neutral-500">Virtual cameras for uploaded footage analysis.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cameras.filter(c => c.source_type !== 'live').map(cam => (
                  <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 shadow-lg flex flex-col hover:border-neutral-700 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-white text-lg flex items-center">
                          {cam.name}
                          <span className="ml-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            Recorded Source
                          </span>
                        </h3>
                        <p className="text-sm text-neutral-400 mt-1">{cam.location}</p>
                      </div>
                      <div className={`px-2 py-1 rounded border text-[10px] font-bold tracking-widest uppercase ${cam.status === 'ONLINE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-neutral-800 text-neutral-500 border-neutral-700'}`}>
                        {cam.status === 'ONLINE' ? 'READY' : 'OFFLINE'}
                      </div>
                    </div>
                    
                    <p className="text-sm text-neutral-500 mb-6 flex-1">{cam.description || "No description provided."}</p>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-neutral-800">
                      <button 
                        onClick={() => toggleStatus(cam)}
                        className={`flex items-center text-sm font-medium transition-colors ${cam.status === 'ONLINE' ? 'text-red-400 hover:text-red-300' : 'text-emerald-400 hover:text-emerald-300'}`}
                      >
                        {cam.status === 'ONLINE' ? (
                          <><Square className="w-4 h-4 mr-1.5" /> Stop</>
                        ) : (
                          <><Play className="w-4 h-4 mr-1.5" /> Start</>
                        )}
                      </button>
                      
                      <div className="flex space-x-2">
                        <button onClick={() => openEdit(cam)} className="p-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-neutral-300 transition-colors">
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleDelete(cam.id)} className="p-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-red-400 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-20 border-2 border-dashed border-neutral-800 rounded-2xl bg-neutral-900/50">
          <CameraIcon className="w-12 h-12 mx-auto mb-4 text-neutral-600" />
          <h3 className="text-lg font-medium text-white mb-2">No cameras registered</h3>
          <p className="text-neutral-500 mb-6 max-w-md mx-auto">Register logical camera sources here before uploading recorded footage or testing queries.</p>
          <button onClick={openCreate} className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-2 rounded-lg transition-all shadow-lg">
            Add First Camera
          </button>
        </div>
      )}
    </div>
  );
}

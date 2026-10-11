"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera, VideoFile } from "@/types";
import { Camera as CameraIcon, Plus, Trash2, Edit2, Play, Square, AlertTriangle, Loader2, Video, X } from "lucide-react";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem('token'));
  }, []);
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ id: "", name: "", location: "", description: "", source_type: "file", stream_url: "" });
  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Delete confirmation state
  const [cameraToDelete, setCameraToDelete] = useState<Camera | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Viewing state
  const [viewingCamera, setViewingCamera] = useState<Camera | null>(null);
  const [cameraFootage, setCameraFootage] = useState<VideoFile[]>([]);
  const [loadingFootage, setLoadingFootage] = useState(false);

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

  const handleDelete = async () => {
    if (!cameraToDelete) return;
    setIsDeleting(true);
    try {
      await api.deleteCamera(cameraToDelete.id);
      setCameras(cameras.filter(c => c.id !== cameraToDelete.id));
      setCameraToDelete(null);
    } catch (err: any) {
      setError(err.message || "Failed to delete camera. It may have associated video footage or active tracking data.");
      setCameraToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const toggleStatus = async (cam: Camera) => {
    try {
      if (cam.status === 'ONLINE' || cam.status === 'RUNNING') {
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

  const openViewer = async (cam: Camera) => {
    setViewingCamera(cam);
    if (cam.source_type !== 'live') {
      setLoadingFootage(true);
      try {
        const footage = await api.getFootage(cam.id);
        setCameraFootage(footage);
      } catch (err: any) {
        console.error("Failed to load footage", err);
      } finally {
        setLoadingFootage(false);
      }
    }
  };

  return (
    <div className="flex flex-col flex-1 w-full relative">
      <main className="flex-1 p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8 animate-in fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-800 mb-2 flex items-center">
              <CameraIcon className="w-8 h-8 mr-3 text-blue-500" />
              Camera Management
            </h1>
            <p className="text-slate-500">Manage logical camera sources for recorded footage ingestion.</p>
          </div>
          <button 
            onClick={openCreate}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-3 rounded-xl transition-all flex items-center shadow-lg shadow-blue-500/20"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Camera
          </button>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start text-rose-600 shadow-sm">
            <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
            <p className="font-medium">{error}</p>
          </div>
        )}

        {showForm && (
          <div className="glass-panel rounded-3xl p-8 shadow-xl mb-8 border border-white/60">
            <h2 className="text-xl font-bold text-slate-800 mb-6">{isEditing ? "Edit Camera" : "Register New Camera"}</h2>
            <form onSubmit={handleSubmit} className="space-y-6 max-w-3xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-slate-600 mb-2">Camera Name</label>
                  <input 
                    required
                    type="text" 
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none transition-all shadow-sm"
                    placeholder="e.g. CAM-01"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-600 mb-2">Location</label>
                  <input 
                    required
                    type="text" 
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none transition-all shadow-sm"
                    placeholder="e.g. Main Gate"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-slate-600 mb-2">Source Type</label>
                  <select 
                    value={formData.source_type}
                    onChange={(e) => setFormData({...formData, source_type: e.target.value})}
                    className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none transition-all shadow-sm"
                  >
                    <option value="file">Recorded Source</option>
                    <option value="live">Live API Stream</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-600 mb-2">Stream URL (Optional)</label>
                  <input 
                    type="text" 
                    value={formData.stream_url}
                    onChange={(e) => setFormData({...formData, stream_url: e.target.value})}
                    className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none transition-all shadow-sm disabled:opacity-50 disabled:bg-slate-50"
                    placeholder="e.g. http://127.0.0.1:8001/health"
                    disabled={formData.source_type !== 'live'}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold text-slate-600 mb-2">Description (Optional)</label>
                <textarea 
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none transition-all shadow-sm h-24 resize-none"
                />
              </div>
              <div className="flex space-x-4 pt-4">
                <button 
                  type="button" 
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl transition-all font-bold shadow-sm flex-1 md:flex-none"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={submitting}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all font-bold flex items-center justify-center shadow-lg shadow-blue-500/20 flex-1 md:flex-none"
                >
                  {submitting ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
                  {isEditing ? "Save Changes" : "Register Camera"}
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1,2,3].map(i => <div key={i} className="h-48 glass-panel rounded-2xl animate-pulse"></div>)}
          </div>
        ) : cameras.length > 0 ? (
          <div className="space-y-12">
            {/* LIVE CAMERAS */}
            {cameras.some(c => c.source_type === 'live') && (
              <div>
                <div className="mb-6 flex items-center">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500 mr-3 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.6)]"></div>
                  <h2 className="text-2xl font-bold text-slate-800">Live API Cameras</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {cameras.filter(c => c.source_type === 'live').map(cam => (
                    <div key={cam.id} className="glass-panel p-6 rounded-3xl flex flex-col hover:shadow-xl transition-all border border-white/60 relative group">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-extrabold text-slate-800 text-xl flex flex-wrap items-center gap-2">
                            <span className="break-words max-w-full">{cam.name}</span>
                            <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest bg-red-100 text-red-600 border border-red-200 whitespace-nowrap shrink-0">
                              Live Source
                            </span>
                          </h3>
                          <p className="text-sm font-medium text-slate-500 mt-1">{cam.location}</p>
                        </div>
                        <div className={`px-2.5 py-1 rounded-md border text-[10px] font-bold tracking-widest uppercase shadow-sm whitespace-nowrap shrink-0 ${(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'bg-emerald-100 text-emerald-600 border-emerald-200' : 'bg-slate-100 text-slate-500 border-slate-200'}`}>
                          {(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'READY' : 'OFFLINE'}
                        </div>
                      </div>
                      
                      <p className="text-sm text-slate-600 mb-8 flex-1 leading-relaxed">{cam.description || "No description provided."}</p>
                      
                      <div className="flex items-center justify-between pt-5 border-t border-slate-100/50">
                        <button 
                          type="button"
                          onClick={() => toggleStatus(cam)}
                          className={`flex items-center text-sm font-bold transition-all px-4 py-2 rounded-xl border ${(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'text-red-600 bg-red-50 border-red-100 hover:bg-red-100' : 'text-emerald-600 bg-emerald-50 border-emerald-100 hover:bg-emerald-100'}`}
                        >
                          {(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? (
                            <><Square className="w-4 h-4 mr-2" fill="currentColor" /> Stop</>
                          ) : (
                            <><Play className="w-4 h-4 mr-2" fill="currentColor" /> Start</>
                          )}
                        </button>
                        
                        <div className="flex space-x-2">
                          <button type="button" onClick={() => openViewer(cam)} className="p-2.5 bg-white hover:bg-purple-50 border border-slate-200 rounded-xl text-slate-600 hover:text-purple-600 transition-colors shadow-sm relative z-10">
                            <Video className="w-4 h-4" />
                          </button>
                          <button type="button" onClick={() => openEdit(cam)} className="p-2.5 bg-white hover:bg-blue-50 border border-slate-200 rounded-xl text-slate-600 hover:text-blue-600 transition-colors shadow-sm relative z-10">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button type="button" onClick={() => setCameraToDelete(cam)} className="p-2.5 bg-white hover:bg-rose-50 border border-slate-200 rounded-xl text-slate-600 hover:text-rose-600 transition-colors shadow-sm relative z-10">
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
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-slate-800">Recorded Sources</h2>
                  <p className="text-sm font-medium text-slate-500 mt-1">Virtual cameras for uploaded footage analysis.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {cameras.filter(c => c.source_type !== 'live').map(cam => (
                    <div key={cam.id} className="glass-panel p-6 rounded-3xl flex flex-col hover:shadow-xl transition-all border border-white/60 relative group">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-extrabold text-slate-800 text-xl flex flex-wrap items-center gap-2">
                            <span className="break-words max-w-full">{cam.name}</span>
                            <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest bg-blue-100 text-blue-600 border border-blue-200 whitespace-nowrap shrink-0">
                              Recorded Source
                            </span>
                          </h3>
                          <p className="text-sm font-medium text-slate-500 mt-1">{cam.location}</p>
                        </div>
                        <div className={`px-2.5 py-1 rounded-md border text-[10px] font-bold tracking-widest uppercase shadow-sm whitespace-nowrap shrink-0 ${(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'bg-emerald-100 text-emerald-600 border-emerald-200' : 'bg-slate-100 text-slate-500 border-slate-200'}`}>
                          {(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'READY' : 'OFFLINE'}
                        </div>
                      </div>
                      
                      <p className="text-sm text-slate-600 mb-8 flex-1 leading-relaxed">{cam.description || "No description provided."}</p>
                      
                      <div className="flex items-center justify-between pt-5 border-t border-slate-100/50">
                        <button 
                          type="button"
                          onClick={() => toggleStatus(cam)}
                          className={`flex items-center text-sm font-bold transition-all px-4 py-2 rounded-xl border ${(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? 'text-red-600 bg-red-50 border-red-100 hover:bg-red-100' : 'text-emerald-600 bg-emerald-50 border-emerald-100 hover:bg-emerald-100'}`}
                        >
                          {(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? (
                            <><Square className="w-4 h-4 mr-2" fill="currentColor" /> Stop</>
                          ) : (
                            <><Play className="w-4 h-4 mr-2" fill="currentColor" /> Start</>
                          )}
                        </button>
                        
                        <div className="flex space-x-2">
                          <button type="button" onClick={() => openViewer(cam)} className="p-2.5 bg-white hover:bg-purple-50 border border-slate-200 rounded-xl text-slate-600 hover:text-purple-600 transition-colors shadow-sm relative z-10">
                            <Video className="w-4 h-4" />
                          </button>
                          <button type="button" onClick={() => openEdit(cam)} className="p-2.5 bg-white hover:bg-blue-50 border border-slate-200 rounded-xl text-slate-600 hover:text-blue-600 transition-colors shadow-sm relative z-10">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button type="button" onClick={() => setCameraToDelete(cam)} className="p-2.5 bg-white hover:bg-rose-50 border border-slate-200 rounded-xl text-slate-600 hover:text-rose-600 transition-colors shadow-sm relative z-10">
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
          <div className="text-center py-24 glass-panel rounded-3xl border border-white/60">
            <CameraIcon className="w-16 h-16 mx-auto mb-6 text-slate-300" />
            <h3 className="text-xl font-bold text-slate-800 mb-3">No cameras registered</h3>
            <p className="text-slate-500 mb-8 max-w-md mx-auto text-lg leading-relaxed">Register logical camera sources here before uploading recorded footage or connecting live streams.</p>
            <button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-blue-500/20">
              Add First Camera
            </button>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {cameraToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
            <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-slate-100 transform transition-all">
              <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center mb-6">
                <AlertTriangle className="w-6 h-6 text-rose-600" />
              </div>
              <h3 className="text-xl font-extrabold text-slate-800 mb-2">Delete Camera</h3>
              <p className="text-slate-500 mb-6 leading-relaxed">
                Are you sure you want to delete <span className="font-bold text-slate-800">{cameraToDelete.name}</span>? This action is permanent and may fail if there are recorded video files associated with it.
              </p>
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setCameraToDelete(null)}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-3 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl font-bold transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-3 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-rose-500/20 flex items-center justify-center disabled:opacity-50"
                >
                  {isDeleting ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Trash2 className="w-4 h-4 mr-2" />}
                  {isDeleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Viewer Modal */}
        {viewingCamera && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
            <div className="bg-white rounded-3xl p-6 max-w-4xl w-full max-h-[90vh] shadow-2xl border border-slate-100 flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-extrabold text-slate-800 flex items-center">
                  <Video className="w-6 h-6 mr-3 text-purple-600" />
                  Viewing: {viewingCamera.name}
                </h3>
                <button onClick={() => setViewingCamera(null)} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500 hover:text-slate-700">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto min-h-0 bg-slate-50 rounded-2xl border border-slate-200 p-4">
                {viewingCamera.source_type === 'live' ? (
                  <div className="w-full h-full flex items-center justify-center min-h-[400px]">
                    {viewingCamera.status === 'ONLINE' ? (
                      <img 
                        src={`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/cameras/${viewingCamera.id}/stream/raw?token=${token}`} 
                        alt="Live Stream" 
                        className="max-w-full max-h-full rounded-xl shadow-lg border border-slate-300" 
                        onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.parentElement!.innerHTML = '<p class="text-slate-500 font-medium">Stream unavailable or failed to connect.</p>'; }}
                      />
                    ) : (
                      <p className="text-slate-500 font-medium text-lg">Camera is offline. Start the camera to view live stream.</p>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {loadingFootage ? (
                      <div className="flex justify-center p-12">
                        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                      </div>
                    ) : cameraFootage.length > 0 ? (
                      cameraFootage.map(video => (
                        <div key={video.id} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-4 items-start">
                          <video 
                            src={`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}${video.file_path}`} 
                            controls 
                            className="w-full md:w-64 rounded-lg bg-black"
                            preload="metadata"
                          />
                          <div>
                            <p className="font-bold text-slate-800">Recorded: {new Date(video.capture_start_utc).toLocaleString()}</p>
                            <p className="text-sm text-slate-500 mt-1">Duration: {video.duration_s ? `${video.duration_s}s` : 'Unknown'}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center p-12">
                        <p className="text-slate-500 font-medium text-lg">No footage uploaded for this camera.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

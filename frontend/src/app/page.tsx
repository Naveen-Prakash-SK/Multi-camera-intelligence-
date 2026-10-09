"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera, QueryResponse } from "@/types";
import { VideoPlayer } from "@/components/VideoPlayer";
import { Search, Activity, Video, CheckCircle, XCircle, Clock, AlertTriangle, Loader2, Database, Camera as CameraIcon, X } from "lucide-react";

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Auth state
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  
  // Chat History state
  const [queryHistory, setQueryHistory] = useState<any[]>([]);
  const [historySearch, setHistorySearch] = useState("");
  
  // Clarification state
  const [needsClarification, setNeedsClarification] = useState(false);
  const [clarificationData, setClarificationData] = useState<any>(null);
  const [selectedCameraId, setSelectedCameraId] = useState("");
  const [recording, setRecording] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<Record<string, 'raw' | 'processed'>>({});

  const [lastQuery, setLastQuery] = useState("");
  const [stats, setStats] = useState({ footage: "--", events: "--" });
  
  // Viewing state
  const [viewingCamera, setViewingCamera] = useState<Camera | null>(null);
  const [cameraFootage, setCameraFootage] = useState<any[]>([]);
  const [loadingFootage, setLoadingFootage] = useState(false);

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

  const handleRecordStream = async (cameraId: string) => {
    setRecording(prev => ({ ...prev, [cameraId]: true }));
    try {
      await api.recordCamera(cameraId, 10);
      alert("Successfully recorded 10s clip. It is now in the processing pipeline!");
    } catch (e: any) {
      alert("Failed to record: " + e.message);
    } finally {
      setRecording(prev => ({ ...prev, [cameraId]: false }));
    }
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    api.getCameras()
      .then(data => {
        const sorted = [...data].sort((a, b) => {
          if (a.source_type === 'live' && b.source_type !== 'live') return -1;
          if (a.source_type !== 'live' && b.source_type === 'live') return 1;
          return 0;
        });
        setCameras(sorted);
      })
      .catch(e => console.error("Failed to load cameras", e));
      
    // Fetch query history
    fetch("http://localhost:8000/api/queries", {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setQueryHistory(data);
      })
      .catch(e => console.error("Failed to load query history", e));

    // Fetch system stats
    fetch("http://localhost:8000/api/stats", {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (data.footage !== undefined) setStats(data);
      })
      .catch(e => console.error("Failed to load stats", e));
  }, [token]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) throw new Error("Invalid credentials");
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
    } catch (err: any) {
      setAuthError(err.message || "Login failed");
    } finally {
      setAuthLoading(false);
    }
  };


  const submitQuery = async (queryText: string, clarificationAnswer?: any) => {
    setLoading(true);
    setError("");
    setNeedsClarification(false);
    setLastQuery(queryText);
    
    try {
      const res = await api.query(queryText, undefined, clarificationAnswer);
      
      if (res.verdict === "CLARIFICATION_REQUIRED") {
        setNeedsClarification(true);
        setClarificationData(res.resolved.clarification_needed);
        setResult(null);
      } else {
        setResult(res);
      }
    } catch (err: any) {
      setError(err.message || "Failed to query the system.");
    } finally {
      setLoading(false);
      // Refresh history
      fetch("http://localhost:8000/api/queries", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data)) setQueryHistory(data);
        });
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    submitQuery(query);
  };

  const handleClarificationSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCameraId) return;
    // Mock backend persistence logic flow: wait, then query
    submitQuery(query, { camera_id: selectedCameraId });
  };

  const exampleQueries = [
    "Did anyone enter the main gate after 9 PM?",
    "Find a red vehicle near the loading dock.",
    "Was a person carrying a bag seen in the lobby?",
    "Show activity around the main gate this morning."
  ];

  if (token === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50 w-full relative">
        <div className="absolute inset-0 bg-blue-500/10 blur-[120px] rounded-full pointer-events-none w-[500px] h-[500px] left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"></div>
        <div className="bg-white/80 backdrop-blur-md p-10 rounded-[2rem] shadow-2xl border border-white/80 w-full max-w-md relative z-10">
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 mb-6">
              <CameraIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Access Portal</h1>
            <p className="text-slate-500 font-medium mt-2">Sign in to view camera feeds</p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            {authError && (
              <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 text-sm font-medium flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                {authError}
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Email Address</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-sm"
                placeholder="admin@gmail.com"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-sm"
                placeholder="••••••••"
                required
              />
            </div>
            <button 
              type="submit" 
              disabled={authLoading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-blue-500/25 flex items-center justify-center disabled:opacity-70"
            >
              {authLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Authenticate"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 w-full relative">
      <main className="flex-1 p-6 lg:p-10 max-w-[1600px] mx-auto w-full space-y-12 pb-24">
        
        {/* TOP SUMMARY */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Cameras</h3>
            <p className="text-3xl font-bold text-slate-800">{cameras.length}</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Footage</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.footage}</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Events</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.events}</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">AI Status</h3>
            <p className="text-3xl font-bold text-emerald-500">READY</p>
          </div>
        </section>

        {/* CHATBOT UI */}
        <section className="relative mt-8 mb-16">
          <div className="absolute inset-0 bg-blue-300/20 blur-[100px] rounded-full pointer-events-none"></div>
          
          <div className="relative glass-panel rounded-[2rem] shadow-2xl overflow-hidden flex flex-col md:flex-row h-[700px] border border-white/80">
            
            {/* Left Sidebar: Searchable History */}
            <div className="w-full md:w-80 bg-white/30 border-b md:border-b-0 md:border-r border-white/50 flex flex-col backdrop-blur-md">
              <div className="p-5 border-b border-white/50">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-widest mb-4 flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-blue-600" />
                  Query History
                </h3>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input 
                    type="text" 
                    placeholder="Search history..." 
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                    className="w-full bg-white/50 border border-white/60 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all shadow-inner"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {queryHistory.filter(h => h.query.toLowerCase().includes(historySearch.toLowerCase())).map((h, i) => (
                  <div 
                    key={h.id || i} 
                    className="p-3 bg-white/40 hover:bg-white/70 border border-white/50 rounded-xl cursor-pointer transition-all shadow-sm hover:shadow group"
                    onClick={() => { setQuery(h.query); submitQuery(h.query); }}
                  >
                    <p className="text-slate-700 font-medium text-sm line-clamp-2 group-hover:text-blue-700 transition-colors">{h.query}</p>
                    <p className="text-[10px] font-bold text-slate-400 mt-2 uppercase tracking-wider">{new Date(h.created_at).toLocaleString()}</p>
                  </div>
                ))}
                {queryHistory.filter(h => h.query.toLowerCase().includes(historySearch.toLowerCase())).length === 0 && (
                  <div className="p-4 text-center text-slate-500 text-sm">No history found.</div>
                )}
              </div>
            </div>

            {/* Right Area: Chatbot Interface */}
            <div className="flex-1 flex flex-col bg-slate-50/30 relative">
              {/* Chat Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 pb-10">
                
                {/* Welcome Message if no query/result */}
                {!result && !loading && !lastQuery && !needsClarification && (
                  <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                     <div className="bg-blue-100 p-4 rounded-full shadow-inner mb-2">
                       <CameraIcon className="w-10 h-10 text-blue-600" />
                     </div>
                     <h2 className="text-2xl font-bold text-slate-800">How can I help you analyze the footage?</h2>
                     <div className="flex flex-wrap justify-center gap-3 max-w-2xl">
                      {exampleQueries.map((ex, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => {setQuery(ex); submitQuery(ex);}}
                          className="text-sm font-medium text-slate-600 bg-white/60 hover:bg-white border border-white/80 px-4 py-2 rounded-xl transition-all shadow-sm hover:shadow-md hover:text-blue-700 text-left"
                        >
                          "{ex}"
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* User Query Bubble */}
                {lastQuery && (
                  <div className="flex justify-end animate-in fade-in slide-in-from-bottom-2">
                    <div className="max-w-[80%] bg-blue-600 text-white p-4 rounded-2xl rounded-tr-sm shadow-md">
                      <p className="text-[15px]">{lastQuery}</p>
                    </div>
                  </div>
                )}

                {/* Loading Bubble */}
                {loading && (
                  <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2">
                    <div className="max-w-[80%] bg-white/80 border border-white p-4 rounded-2xl rounded-tl-sm shadow-md flex items-center space-x-3">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                      <p className="text-[15px] text-slate-600 font-medium">Analyzing indexed footage across all cameras...</p>
                    </div>
                  </div>
                )}

                {/* Error Bubble */}
                {error && (
                  <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2">
                    <div className="max-w-[80%] bg-red-50 border border-red-100 p-4 rounded-2xl rounded-tl-sm shadow-md flex items-start space-x-3">
                      <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                      <p className="text-[15px] text-red-700">{error}</p>
                    </div>
                  </div>
                )}
                
                {/* Clarification Bubble */}
                {needsClarification && clarificationData && !loading && (
                  <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 w-full">
                    <div className="max-w-[90%] md:max-w-[70%] bg-white/80 backdrop-blur-md border border-amber-200 p-6 rounded-3xl rounded-tl-sm shadow-xl space-y-5">
                      <div className="flex items-center space-x-3 text-amber-600 border-b border-amber-100 pb-3">
                        <Database className="w-5 h-5" />
                        <span className="font-bold">Clarification Needed</span>
                      </div>
                      
                      <p className="text-slate-700 text-[15px]">
                        I don't have enough context for <span className="font-bold text-slate-900 bg-amber-100 px-2 py-0.5 rounded-md">"{clarificationData.entity_name}"</span>. 
                        Which camera does this refer to?
                      </p>
                      
                      <div className="space-y-2 mt-4 max-h-60 overflow-y-auto">
                        {cameras.map(cam => (
                          <button 
                            key={cam.id}
                            onClick={() => {
                              setSelectedCameraId(cam.id);
                              submitQuery(lastQuery, { camera_id: cam.id });
                            }}
                            className="w-full text-left p-3 border border-slate-200 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all flex justify-between items-center group"
                          >
                            <div>
                              <p className="font-bold text-slate-800">{cam.name}</p>
                              <p className="text-xs text-slate-500">{cam.location}</p>
                            </div>
                            <div className="w-6 h-6 rounded-full border border-slate-300 group-hover:border-blue-500 group-hover:bg-blue-500 flex items-center justify-center transition-colors">
                              <CheckCircle className="w-4 h-4 text-white opacity-0 group-hover:opacity-100" />
                            </div>
                          </button>
                        ))}
                      </div>
                      <button 
                        onClick={() => setNeedsClarification(false)}
                        className="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors uppercase tracking-widest mt-2"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Result Bubble (Intelligence Report) */}
                {result && !needsClarification && !loading && (
                  <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 w-full">
                    <div className="max-w-[95%] xl:max-w-[85%] w-full bg-white/80 backdrop-blur-md border border-white p-6 rounded-3xl rounded-tl-sm shadow-xl space-y-6">
                      
                      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                            <Activity className="w-4 h-4 text-blue-600" />
                          </div>
                          <span className="font-bold text-slate-700">AI Analysis Report</span>
                        </div>
                        {result.verdict === 'YES' ? (
                          <div className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-bold flex items-center shadow-sm">
                            <CheckCircle className="w-4 h-4 mr-1.5" /> MATCH FOUND
                          </div>
                        ) : (
                          <div className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-bold flex items-center shadow-sm">
                            <XCircle className="w-4 h-4 mr-1.5" /> NO MATCH
                          </div>
                        )}
                      </div>

                      {result.verdict === 'YES' ? (
                        <div className="space-y-6">
                          <p className="text-lg font-bold text-slate-800 leading-relaxed">
                            {result.answer || "Event detected in indexed footage."}
                          </p>
                          
                          {result.results.length > 0 && (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                              <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                  <div className="bg-slate-50/50 p-3 rounded-xl border border-slate-100">
                                    <p className="text-[10px] text-slate-400 uppercase tracking-wider font-bold mb-1">Camera</p>
                                    <p className="text-sm font-semibold text-slate-700 flex items-center">
                                      <CameraIcon className="w-3 h-3 mr-1.5 text-slate-400" />
                                      {result.results[0].camera_name || "Unknown"}
                                    </p>
                                  </div>
                                  <div className="bg-slate-50/50 p-3 rounded-xl border border-slate-100">
                                    <p className="text-[10px] text-slate-400 uppercase tracking-wider font-bold mb-1">Timestamp</p>
                                    <p className="text-sm font-semibold text-slate-700 flex items-center">
                                      <Clock className="w-3 h-3 mr-1.5 text-slate-400" />
                                      {new Date(result.results[0].timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                                    </p>
                                  </div>
                                </div>
                                
                                <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100/50">
                                  <p className="text-[10px] text-blue-400 uppercase tracking-wider font-bold mb-2">Visual Verification</p>
                                  <p className="text-sm text-slate-700 font-medium italic leading-relaxed">
                                    "{result.results[0].attributes?.vlm_reason || "The event matches the requested visual characteristics based on semantic video indexing."}"
                                  </p>
                                </div>
                              </div>
                              
                              <div className="bg-black rounded-xl border-2 border-slate-800 overflow-hidden shadow-md relative min-h-[200px]">
                                <VideoPlayer 
                                  streamUrl={result.results[0]?.evidence.clip_url}
                                  thumbnailUrl={result.results[0]?.evidence.thumbnail_url}
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="py-4 text-slate-600 font-medium">
                          <p>I searched through the indexed footage but could not find any events matching your description with high confidence.</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

              </div>

              {/* Input Area */}
              <div className="p-4 md:p-6 bg-white/60 backdrop-blur-md border-t border-white/80 mt-auto">
                <form onSubmit={handleSearch} className="relative flex items-end gap-3 max-w-4xl mx-auto">
                  <div className="relative flex-1 group">
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSearch(e as any);
                        }
                      }}
                      placeholder="Ask about a vehicle, person, or event..." 
                      className="w-full bg-white border border-slate-200 rounded-2xl pl-5 pr-12 py-4 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-[15px] shadow-sm resize-none min-h-[60px] max-h-[200px]"
                      rows={1}
                    />
                  </div>
                  <button 
                    type="submit" 
                    disabled={loading || !query.trim()}
                    className="bg-blue-600 hover:bg-blue-500 text-white p-4 rounded-2xl transition-all disabled:opacity-50 flex items-center justify-center shadow-md hover:shadow-blue-500/25 shrink-0 h-[60px] w-[60px]"
                  >
                    {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
                  </button>
                </form>
                <p className="text-center text-[11px] text-slate-400 font-medium mt-3 uppercase tracking-widest">
                  Natural Language AI Search Powered By Qwen-VL & SigLIP
                </p>
              </div>
              
            </div>
          </div>
        </section>

                {/* CAMERA SOURCES */}
        <section>
          {cameras.length > 0 ? (
            <div className="space-y-12">
              {/* LIVE CAMERAS */}
              {cameras.some(c => c.source_type === 'live') && (
                <div>
                  <div className="mb-6 flex items-center">
                    <div className="w-3 h-3 rounded-full bg-red-500 mr-3 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.6)]"></div>
                    <h2 className="text-2xl font-bold text-slate-800">Live Cameras</h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {cameras.filter(c => c.source_type === 'live').map(cam => (
                  <div key={cam.id} className="glass-panel rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all group/card">
                    <div className="p-5 border-b border-white/50 flex justify-between items-start bg-white/40 backdrop-blur-sm">
                      <div>
                        <h3 className="text-sm font-bold text-slate-700 font-mono tracking-tight">{cam.id.split('-')[0].toUpperCase()}</h3>
                        <div className="flex items-center mt-2">
                          <div className="h-2 w-2 bg-emerald-500 rounded-full mr-2"></div>
                          <span className="text-[10px] font-bold text-slate-500 tracking-wider uppercase">READY</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest bg-red-100 text-red-600 border border-red-200 shadow-sm">
                          Live Source
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-slate-900 flex flex-col items-center justify-center text-slate-500 relative overflow-hidden group">
                      {(cam.status === 'ONLINE' || cam.status === 'RUNNING') ? (
                        <>
                          <img 
                            src={`http://localhost:8000/api/cameras/${cam.id}/stream/${viewMode[cam.id] || 'processed'}?token=${token}`} 
                            alt={`${cam.name} stream`} 
                            className="w-full h-full object-cover" 
                          />
                          <div className="absolute top-2 right-2 flex bg-black/50 backdrop-blur-sm rounded-lg p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button 
                              onClick={() => setViewMode(prev => ({...prev, [cam.id]: 'raw'}))}
                              className={`px-3 py-1 text-xs font-bold rounded-md ${(!viewMode[cam.id] || viewMode[cam.id] === 'raw') ? 'bg-white text-black' : 'text-white hover:bg-white/20'}`}
                            >
                              RAW
                            </button>
                            <button 
                              onClick={() => setViewMode(prev => ({...prev, [cam.id]: 'processed'}))}
                              className={`px-3 py-1 text-xs font-bold rounded-md ${(viewMode[cam.id] === 'processed') ? 'bg-white text-black' : 'text-white hover:bg-white/20'}`}
                            >
                              PROCESSED
                            </button>
                          </div>
                        </>
                      ) : (
                        <>
                          <Video className="w-12 h-12 mb-4 opacity-30" />
                          <span className="text-lg tracking-widest font-mono font-bold text-slate-400">NO SIGNAL</span>
                          <span className="text-xs text-slate-500 mt-2">Live stream unavailable</span>
                        </>
                      )}
                    </div>
                    <div className="p-5 flex justify-between items-center bg-white/20 backdrop-blur-sm border-t border-white/50">
                      <div>
                        <p className="text-base font-bold text-slate-800">{cam.name}</p>
                        <p className="text-sm text-slate-500 mt-0.5">{cam.location}</p>
                      </div>
                      <button 
                        onClick={() => handleRecordStream(cam.id)}
                        disabled={recording[cam.id]}
                        className="px-4 py-2 bg-white hover:bg-slate-50 text-red-600 border border-slate-200 shadow-sm hover:shadow rounded-xl text-xs font-bold tracking-wider transition-all disabled:opacity-50 flex items-center"
                      >
                        {recording[cam.id] ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <div className="w-2.5 h-2.5 rounded-full bg-red-500 mr-2 animate-pulse" />}
                        {recording[cam.id] ? "RECORDING..." : "REC 10S"}
                      </button>
                    </div>
                  </div>
                    ))}
                  </div>
                </div>
              )}

              {/* RECORDED CAMERAS */}
              {cameras.some(c => c.source_type !== 'live') && (
                <div className="pt-12 mt-12 border-t border-slate-200">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-slate-800">Recorded Sources</h2>
                    <p className="text-base text-slate-500 mt-1">Registered virtual sources and indexed footage</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {cameras.filter(c => c.source_type !== 'live').map(cam => (
                  <div key={cam.id} className="glass-panel rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all">
                    <div className="p-5 border-b border-white/50 flex justify-between items-start bg-white/40 backdrop-blur-sm">
                      <div>
                        <h3 className="text-sm font-bold text-slate-700 font-mono tracking-tight">{cam.id.split('-')[0].toUpperCase()}</h3>
                        <div className="flex items-center mt-2">
                          <div className="h-2 w-2 bg-slate-300 rounded-full mr-2"></div>
                          <span className="text-[10px] font-bold text-slate-500 tracking-wider uppercase">READY</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          Recorded Source
                        </span>
                      </div>
                    </div>
                    <div className="aspect-video bg-slate-100 flex flex-col items-center justify-center text-slate-500 relative border-b border-white/50 overflow-hidden">
                      <Video className="w-12 h-12 mb-4 opacity-30" />
                      <span className="text-lg tracking-widest font-mono font-bold text-slate-400">NO SIGNAL</span>
                      <span className="text-xs text-slate-500 mt-2">Recorded footage only</span>
                    </div>
                    <div className="p-5 flex justify-between items-center bg-white/20 backdrop-blur-sm">
                      <div>
                        <p className="text-base font-bold text-slate-800">{cam.name}</p>
                        <p className="text-sm text-slate-500 mt-0.5">{cam.location}</p>
                      </div>
                      <button onClick={() => openViewer(cam)} className="px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-600 border border-purple-200 shadow-sm hover:shadow rounded-xl text-xs font-bold tracking-wider transition-all flex items-center">
                        <Video className="w-4 h-4 mr-2" />
                        VIEW
                      </button>
                    </div>
                  </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-64 border border-dashed border-slate-300 rounded-3xl flex flex-col items-center justify-center text-center bg-white/40 backdrop-blur-sm shadow-sm">
              <CameraIcon className="w-12 h-12 text-slate-400 mb-4" />
              <h3 className="text-xl font-bold text-slate-800 mb-2">NO CAMERA SOURCES</h3>
              <p className="text-slate-500 mb-6 max-w-sm">Register a camera to begin indexing CCTV footage.</p>
            </div>
          )}
        </section>

      </main>

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
    </div>
  );
}

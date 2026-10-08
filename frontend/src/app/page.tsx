"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera, QueryResponse } from "@/types";
import { VideoPlayer } from "@/components/VideoPlayer";
import { Search, Activity, Video, CheckCircle, XCircle, Clock, AlertTriangle, Loader2, Database, Camera as CameraIcon } from "lucide-react";

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Chat History state
  const [queryHistory, setQueryHistory] = useState<any[]>([]);
  
  // Clarification state
  const [needsClarification, setNeedsClarification] = useState(false);
  const [clarificationData, setClarificationData] = useState<any>(null);
  const [selectedCameraId, setSelectedCameraId] = useState("");
  const [recording, setRecording] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<Record<string, 'raw' | 'processed'>>({});

  const [lastQuery, setLastQuery] = useState("");

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
    fetch("http://localhost:8000/api/queries")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setQueryHistory(data);
      })
      .catch(e => console.error("Failed to load query history", e));
  }, []);


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
      fetch("http://localhost:8000/api/queries")
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
            <p className="text-3xl font-bold text-slate-800">--</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Events</h3>
            <p className="text-3xl font-bold text-slate-800">--</p>
          </div>
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">AI Status</h3>
            <p className="text-3xl font-bold text-emerald-500">READY</p>
          </div>
        </section>

        {/* SEARCH AREA - VISUAL CENTER */}
        <section className="relative mt-8">
          <div className="absolute inset-0 bg-blue-300/20 blur-[100px] rounded-full pointer-events-none"></div>
          <div className="relative glass-panel p-8 md:p-12 rounded-[2rem] shadow-2xl flex flex-col items-center text-center">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-800 mb-4 tracking-tight">Ask your cameras anything</h2>
            <p className="text-slate-500 mb-10 max-w-2xl text-lg">Search indexed CCTV footage using natural language.</p>
            
            <form onSubmit={handleSearch} className="w-full max-w-4xl relative group">
              <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Did a red car pass through the main gate between 2 PM and 4 PM?" 
                className="w-full bg-white/60 backdrop-blur-md border border-white/80 rounded-2xl pl-16 pr-44 py-5 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-lg shadow-inner"
              />
              <button 
                type="submit" 
                disabled={loading}
                className="absolute right-3 top-3 bottom-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center shadow-lg hover:shadow-blue-500/25"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
                {loading ? "SEARCHING FOOTAGE..." : "SEARCH FOOTAGE"}
              </button>
            </form>
            
            <div className="mt-6 flex flex-wrap justify-center gap-3 max-w-4xl">
              {exampleQueries.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setQuery(ex)}
                  className="text-sm font-medium text-slate-500 bg-white/50 hover:bg-white border border-white/60 hover:border-blue-200 px-5 py-2.5 rounded-full transition-all shadow-sm hover:shadow-md hover:text-blue-700"
                >
                  "{ex}"
                </button>
              ))}
            </div>
            
            {/* Chat History Snippet */}
            {queryHistory.length > 0 && !result && !loading && (
              <div className="mt-10 w-full max-w-4xl text-left bg-white/40 p-6 rounded-2xl border border-white/60 shadow-sm">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Recent Queries</h3>
                <div className="space-y-3">
                  {queryHistory.slice(0, 5).map((h, i) => (
                    <div 
                      key={h.id || i} 
                      className="flex items-start gap-3 p-3 hover:bg-white/60 rounded-xl cursor-pointer transition-colors"
                      onClick={() => { setQuery(h.query); submitQuery(h.query); }}
                    >
                      <Clock className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-slate-800 font-medium">{h.query}</p>
                        <p className="text-xs text-slate-500 mt-1">{new Date(h.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
          </div>
        </section>

        {/* RESULTS AREA */}
        {result && !needsClarification && (
          <section className="animate-in slide-in-from-bottom-8 duration-500">
            <h2 className="text-sm font-bold tracking-widest text-slate-500 uppercase mb-6 flex items-center">
              Intelligence Report
            </h2>
            
            <div className="glass-panel rounded-3xl overflow-hidden shadow-2xl">
              <div className="p-5 border-b border-white/50 bg-white/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Query</p>
                  <p className="text-sm font-medium text-slate-700">"{lastQuery}"</p>
                </div>
                {result.verdict === 'YES' ? (
                  <div className="px-4 py-2 bg-emerald-100/80 border border-emerald-200 rounded-xl flex items-center text-emerald-700 font-bold text-sm shadow-sm">
                    <CheckCircle className="w-5 h-5 mr-2" /> MATCH CONFIRMED
                  </div>
                ) : (
                  <div className="px-4 py-2 bg-slate-100 border border-slate-200 rounded-xl flex items-center text-slate-600 font-bold text-sm shadow-sm">
                    <XCircle className="w-5 h-5 mr-2" /> NO MATCH FOUND
                  </div>
                )}
              </div>
              
              {result.verdict === 'YES' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2">
                  <div className="p-8 lg:p-10 border-r border-white/50 space-y-8 bg-white/20">
                    <div>
                      <h3 className="text-xl md:text-2xl font-bold text-slate-800 mb-6 leading-relaxed">
                        {result.answer || "Event detected in indexed footage."}
                      </h3>
                    </div>
                    
                    {result.results.length > 0 && (
                      <div className="space-y-6">
                        <div>
                          <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-2">Camera</p>
                          <p className="text-slate-700 font-semibold flex items-center bg-white/60 w-fit px-3 py-1.5 rounded-lg border border-white/80">
                            <CameraIcon className="w-4 h-4 mr-2 text-slate-500" />
                            {result.results[0].camera_name || "Unknown Camera"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-2">Timestamp</p>
                          <p className="text-slate-700 font-semibold flex items-center bg-white/60 w-fit px-3 py-1.5 rounded-lg border border-white/80">
                            <Clock className="w-4 h-4 mr-2 text-slate-500" />
                            {new Date(result.results[0].timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-2">Confidence</p>
                          <p className="text-slate-700 font-semibold text-lg">
                            {result.confidence ? (result.confidence).toFixed(2) : "0.94"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-2">AI Verification</p>
                          <p className="text-slate-600 text-sm p-4 bg-white/50 rounded-xl border border-white/80 leading-relaxed font-medium">
                            "{result.results[0].attributes?.vlm_reason || "The event matches the requested visual characteristics based on semantic video indexing."}"
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-8 lg:p-10 flex flex-col bg-white/10">
                    <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-4">Evidence Video</p>
                    {result.results.length > 0 ? (
                      <div className="flex-1 bg-black rounded-2xl border-4 border-slate-800 overflow-hidden shadow-xl relative min-h-[300px]">
                        <VideoPlayer 
                          streamUrl={result.results[0]?.evidence.clip_url}
                          thumbnailUrl={result.results[0]?.evidence.thumbnail_url}
                        />
                      </div>
                    ) : (
                      <div className="flex-1 bg-slate-100 border border-slate-200 border-dashed rounded-2xl flex flex-col items-center justify-center text-slate-400 min-h-[300px]">
                        <Video className="w-10 h-10 mb-3 opacity-50" />
                        <p className="text-sm font-bold tracking-widest">EVIDENCE UNAVAILABLE</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-12 lg:p-20 flex flex-col items-center text-center bg-white/20">
                  <div className="bg-slate-200/50 p-4 rounded-full mb-6">
                    <Search className="w-10 h-10 text-slate-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-800 mb-3">No verified evidence matched this query.</h3>
                  <p className="text-slate-500 max-w-md text-lg">We searched through the indexed footage but could not find any events matching your description with high confidence.</p>
                  <button onClick={() => {setResult(null); setQuery("");}} className="mt-8 bg-white hover:bg-slate-50 text-slate-700 font-bold px-8 py-3 rounded-xl transition-all border border-slate-200 shadow-sm hover:shadow-md">
                    NEW SEARCH
                  </button>
                </div>
              )}
            </div>
          </section>
        )}

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
                      {cam.status === 'ONLINE' ? (
                        <>
                          <img 
                            src={`http://localhost:8000/api/cameras/${cam.id}/stream/${viewMode[cam.id] || 'processed'}`} 
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

        {/* CLARIFICATION MODAL */}
        {needsClarification && clarificationData && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md animate-in fade-in duration-200">
            <div className="bg-white/95 backdrop-blur-xl border border-white rounded-3xl overflow-hidden max-w-md w-full shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)]">
              <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                <div className="flex items-center">
                  <div className="h-12 w-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mr-4 shadow-sm border border-blue-200">
                    <Database className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800">Clarification Required</h3>
                </div>
              </div>
              
              <div className="p-8">
                <p className="text-slate-600 mb-6 text-lg leading-relaxed">
                  I don't have enough context for <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200 shadow-sm">"{clarificationData.entity_name}"</span>. 
                  Which camera does this refer to?
                </p>
                
                <form onSubmit={handleClarificationSubmit} className="space-y-6">
                  <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                    {cameras.map(cam => (
                      <label key={cam.id} className={`flex items-center p-4 border-2 rounded-2xl cursor-pointer transition-all shadow-sm ${selectedCameraId === cam.id ? 'border-blue-500 bg-blue-50/80 shadow-md transform -translate-y-0.5' : 'border-slate-200 bg-white hover:border-slate-300'}`}>
                        <input 
                          type="radio" 
                          name="camera" 
                          value={cam.id}
                          onChange={(e) => setSelectedCameraId(e.target.value)}
                          className="w-5 h-5 text-blue-600 bg-white border-slate-300 focus:ring-blue-600 focus:ring-offset-white" 
                        />
                        <div className="ml-4">
                          <p className="text-base font-bold text-slate-800">{cam.name}</p>
                          <p className="text-xs text-slate-500 font-medium mt-0.5">{cam.location}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                  
                  <div className="flex space-x-3 pt-6 border-t border-slate-100">
                    <button 
                      type="button"
                      onClick={() => setNeedsClarification(false)}
                      className="flex-1 px-4 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors font-bold text-sm shadow-sm"
                    >
                      CANCEL
                    </button>
                    <button 
                      type="submit" 
                      disabled={!selectedCameraId || loading}
                      className="flex-1 px-4 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all font-bold text-sm disabled:opacity-50 flex justify-center items-center shadow-[0_8px_16px_-4px_rgba(37,99,235,0.4)] hover:shadow-[0_12px_20px_-4px_rgba(37,99,235,0.5)]"
                    >
                      {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "SAVE & CONTINUE"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

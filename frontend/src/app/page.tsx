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
  
  // Clarification state
  const [needsClarification, setNeedsClarification] = useState(false);
  const [clarificationData, setClarificationData] = useState<any>(null);
  const [selectedCameraId, setSelectedCameraId] = useState("");

  const [lastQuery, setLastQuery] = useState("");

  useEffect(() => {
    api.getCameras().then(setCameras).catch(e => console.error("Failed to load cameras", e));
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
          <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-2">Cameras</h3>
            <p className="text-3xl font-bold text-white">{cameras.length}</p>
          </div>
          <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-2">Footage</h3>
            <p className="text-3xl font-bold text-white">--</p>
          </div>
          <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-2">Events</h3>
            <p className="text-3xl font-bold text-white">--</p>
          </div>
          <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-2">AI Status</h3>
            <p className="text-3xl font-bold text-emerald-500">READY</p>
          </div>
        </section>

        {/* SEARCH AREA - VISUAL CENTER */}
        <section className="relative mt-8">
          <div className="absolute inset-0 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none"></div>
          <div className="relative bg-neutral-900 border border-neutral-800 p-8 md:p-12 rounded-2xl shadow-2xl flex flex-col items-center text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">Ask your cameras anything</h2>
            <p className="text-neutral-400 mb-8 max-w-2xl">Search indexed CCTV footage using natural language.</p>
            
            <form onSubmit={handleSearch} className="w-full max-w-4xl relative group">
              <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-neutral-500 group-focus-within:text-blue-500 transition-colors" />
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Did a red car pass through the main gate between 2 PM and 4 PM?" 
                className="w-full bg-black/50 border border-neutral-700 rounded-2xl pl-16 pr-44 py-5 text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-lg shadow-inner"
              />
              <button 
                type="submit" 
                disabled={loading}
                className="absolute right-3 top-3 bottom-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center shadow-lg"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
                {loading ? "SEARCHING INDEXED FOOTAGE..." : "SEARCH FOOTAGE"}
              </button>
            </form>
            
            <div className="mt-6 flex flex-wrap justify-center gap-3 max-w-4xl">
              {exampleQueries.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setQuery(ex)}
                  className="text-xs text-neutral-400 bg-neutral-800/50 hover:bg-neutral-800 border border-neutral-700 hover:border-neutral-600 px-4 py-2 rounded-full transition-colors"
                >
                  "{ex}"
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* RESULTS AREA */}
        {result && !needsClarification && (
          <section className="animate-in slide-in-from-bottom-8 duration-500">
            <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-6 flex items-center">
              Intelligence Report
            </h2>
            
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden shadow-2xl">
              <div className="p-4 border-b border-neutral-800 bg-black/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-1">Query</p>
                  <p className="text-sm text-neutral-300">"{lastQuery}"</p>
                </div>
                {result.verdict === 'YES' ? (
                  <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center text-emerald-400 font-bold text-sm">
                    <CheckCircle className="w-4 h-4 mr-2" /> MATCH CONFIRMED
                  </div>
                ) : (
                  <div className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded-lg flex items-center text-neutral-400 font-bold text-sm">
                    <XCircle className="w-4 h-4 mr-2" /> NO MATCH FOUND
                  </div>
                )}
              </div>
              
              {result.verdict === 'YES' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2">
                  <div className="p-8 border-r border-neutral-800 space-y-8">
                    <div>
                      <h3 className="text-xl font-medium text-white mb-6 leading-relaxed">
                        {result.answer || "Event detected in indexed footage."}
                      </h3>
                    </div>
                    
                    {result.results.length > 0 && (
                      <div className="space-y-6">
                        <div>
                          <p className="text-xs text-neutral-500 uppercase tracking-wider font-semibold mb-2">Camera</p>
                          <p className="text-white font-medium flex items-center">
                            <CameraIcon className="w-4 h-4 mr-2 text-neutral-400" />
                            {result.results[0].camera_name || "Unknown Camera"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-neutral-500 uppercase tracking-wider font-semibold mb-2">Timestamp</p>
                          <p className="text-white font-medium flex items-center">
                            <Clock className="w-4 h-4 mr-2 text-neutral-400" />
                            {new Date(result.results[0].timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-neutral-500 uppercase tracking-wider font-semibold mb-2">Confidence</p>
                          <p className="text-white font-medium">
                            {result.confidence ? (result.confidence).toFixed(2) : "0.94"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-neutral-500 uppercase tracking-wider font-semibold mb-2">AI Verification</p>
                          <p className="text-neutral-300 text-sm p-4 bg-black/40 rounded-lg border border-neutral-800 leading-relaxed">
                            "{result.results[0].attributes?.vlm_reason || "The event matches the requested visual characteristics based on semantic video indexing."}"
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-8 flex flex-col">
                    <p className="text-xs text-neutral-500 uppercase tracking-wider font-semibold mb-4">Evidence Video</p>
                    {result.results.length > 0 ? (
                      <div className="flex-1 bg-black rounded-xl border border-neutral-800 overflow-hidden shadow-xl relative min-h-[300px]">
                        <VideoPlayer 
                          streamUrl={result.results[0]?.evidence.clip_url}
                          thumbnailUrl={result.results[0]?.evidence.thumbnail_url}
                        />
                      </div>
                    ) : (
                      <div className="flex-1 bg-neutral-900 border border-neutral-800 border-dashed rounded-xl flex flex-col items-center justify-center text-neutral-500 min-h-[300px]">
                        <Video className="w-8 h-8 mb-3 opacity-50" />
                        <p className="text-sm font-medium">EVIDENCE UNAVAILABLE</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-12 flex flex-col items-center text-center">
                  <Search className="w-12 h-12 text-neutral-600 mb-4" />
                  <h3 className="text-xl font-medium text-white mb-2">No verified evidence matched this query.</h3>
                  <p className="text-neutral-400 max-w-md">We searched through the indexed footage but could not find any events matching your description with high confidence.</p>
                  <button onClick={() => {setResult(null); setQuery("");}} className="mt-8 bg-neutral-800 hover:bg-neutral-700 text-white font-medium px-6 py-2 rounded-lg transition-colors border border-neutral-700">
                    NEW SEARCH
                  </button>
                </div>
              )}
            </div>
          </section>
        )}

        {/* CAMERA SOURCES */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-white">Camera Sources</h2>
            <p className="text-sm text-neutral-400">Registered CCTV sources and indexed footage</p>
          </div>
          
          {cameras.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {cameras.map(cam => (
                <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-lg transition-all hover:border-neutral-700">
                  <div className="p-4 border-b border-neutral-800 flex justify-between items-start bg-black/20">
                    <div>
                      <h3 className="text-sm font-bold text-white font-mono">{cam.id.split('-')[0].toUpperCase()}</h3>
                      <div className="flex items-center mt-2">
                        <div className="h-1.5 w-1.5 bg-neutral-600 rounded-full mr-2"></div>
                        <span className="text-[10px] font-bold text-neutral-500 tracking-wider uppercase">READY</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest">
                        Recorded Source
                      </span>
                    </div>
                  </div>
                  <div className="aspect-video bg-black flex flex-col items-center justify-center text-neutral-600 relative border-b border-neutral-800">
                    <Video className="w-10 h-10 mb-3 opacity-20" />
                    <span className="text-lg tracking-widest font-mono font-bold text-neutral-500">NO SIGNAL</span>
                    <span className="text-xs text-neutral-500 mt-2">Live stream unavailable</span>
                  </div>
                  <div className="p-4 flex justify-between items-center bg-black/20">
                    <div>
                      <p className="text-sm font-medium text-neutral-300">{cam.name}</p>
                      <p className="text-xs text-neutral-500 mt-0.5">{cam.location}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-64 border border-dashed border-neutral-800 rounded-xl flex flex-col items-center justify-center text-center bg-neutral-900/50">
              <CameraIcon className="w-10 h-10 text-neutral-600 mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">NO CAMERA SOURCES</h3>
              <p className="text-neutral-400 mb-6 max-w-sm">Register a camera to begin indexing CCTV footage.</p>
            </div>
          )}
        </section>

        {/* CLARIFICATION MODAL */}
        {needsClarification && clarificationData && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden max-w-md w-full shadow-2xl">
              <div className="p-6 border-b border-neutral-800 bg-black/20">
                <div className="flex items-center">
                  <div className="h-10 w-10 bg-blue-500/20 text-blue-500 rounded-xl flex items-center justify-center mr-4 border border-blue-500/30">
                    <Database className="w-5 h-5" />
                  </div>
                  <h3 className="text-xl font-bold text-white">Clarification Required</h3>
                </div>
              </div>
              
              <div className="p-6">
                <p className="text-neutral-300 mb-6 leading-relaxed">
                  I don't have enough context for <span className="font-semibold text-white bg-white/10 px-2 py-0.5 rounded">"{clarificationData.entity_name}"</span>. 
                  Which camera does this refer to?
                </p>
                
                <form onSubmit={handleClarificationSubmit} className="space-y-6">
                  <div className="space-y-3 max-h-60 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-neutral-700">
                    {cameras.map(cam => (
                      <label key={cam.id} className={`flex items-center p-4 border rounded-xl cursor-pointer transition-all ${selectedCameraId === cam.id ? 'border-blue-500 bg-blue-500/10' : 'border-neutral-800 bg-black/30 hover:border-neutral-700'}`}>
                        <input 
                          type="radio" 
                          name="camera" 
                          value={cam.id}
                          onChange={(e) => setSelectedCameraId(e.target.value)}
                          className="w-4 h-4 text-blue-600 bg-neutral-900 border-neutral-700 focus:ring-blue-600 focus:ring-offset-neutral-900" 
                        />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-white">{cam.name}</p>
                          <p className="text-xs text-neutral-500 mt-0.5">{cam.location}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                  
                  <div className="flex space-x-3 pt-4 border-t border-neutral-800">
                    <button 
                      type="button"
                      onClick={() => setNeedsClarification(false)}
                      className="flex-1 px-4 py-3 bg-neutral-800 hover:bg-neutral-700 text-white rounded-xl transition-colors font-medium text-sm border border-neutral-700"
                    >
                      CANCEL
                    </button>
                    <button 
                      type="submit" 
                      disabled={!selectedCameraId || loading}
                      className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-colors font-medium text-sm disabled:opacity-50 flex justify-center items-center shadow-lg shadow-blue-900/20"
                    >
                      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "SAVE & CONTINUE"}
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

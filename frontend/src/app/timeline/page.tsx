"use client";

import { useState } from "react";
import { api } from "@/lib/api/client";
import { Clock, Search, AlertTriangle, ChevronRight, CheckCircle, Activity, Camera } from "lucide-react";

export default function TimelinePage() {
  const [globalId, setGlobalId] = useState("");
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!globalId.trim()) return;
    
    setLoading(true);
    setError("");
    setTimelineData(null);
    
    try {
      const data = await api.getTimeline(globalId.trim());
      setTimelineData(data);
    } catch (err: any) {
      setError(err.message || "Failed to load timeline.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 w-full relative">
      <main className="flex-1 p-6 lg:p-10 max-w-[1000px] mx-auto w-full space-y-12 pb-24 animate-in fade-in">
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold text-slate-800 flex items-center">
            <Clock className="w-8 h-8 mr-3 text-blue-600" />
            Cross-Camera Timeline
          </h1>
          <p className="text-slate-500 text-lg">Track an identified object or person chronologically across the camera network.</p>
        </div>

        <div className="glass-panel rounded-[2rem] p-8 md:p-12 shadow-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-blue-300/10 blur-[50px] rounded-full pointer-events-none"></div>
          <form onSubmit={handleSearch} className="relative flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="relative flex-1 group">
              <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input 
                type="text" 
                value={globalId}
                onChange={(e) => setGlobalId(e.target.value)}
                placeholder="Enter Global Track ID (e.g., uuid...)" 
                className="w-full bg-white/60 backdrop-blur-md border border-white/80 rounded-2xl pl-16 pr-4 py-4 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-lg shadow-inner"
              />
            </div>
            <button 
              type="submit" 
              disabled={loading || !globalId.trim()}
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-10 py-4 rounded-2xl transition-all disabled:opacity-50 min-w-[140px] shadow-lg hover:shadow-blue-500/25 flex items-center justify-center"
            >
              {loading ? "Searching..." : "Trace"}
            </button>
          </form>
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-100 rounded-xl flex items-start text-red-600 shadow-sm relative z-10">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}
        </div>

        {timelineData && (
          <div className="glass-panel rounded-[2rem] p-8 shadow-2xl relative overflow-hidden">
            <div className="mb-8 border-b border-white/50 pb-6 flex justify-between items-end">
              <div>
                <p className="text-xs font-bold text-slate-400 tracking-widest uppercase mb-1">Global Track ID</p>
                <p className="text-xl font-mono text-slate-800 break-all bg-white/50 px-4 py-2 rounded-xl border border-white/80 inline-block shadow-sm">{timelineData.global_identity_id}</p>
              </div>
              {timelineData.insufficient_evidence && (
                <span className="bg-amber-100 text-amber-700 border border-amber-200 px-4 py-2 rounded-xl text-xs font-bold flex items-center shadow-sm">
                  <AlertTriangle className="w-4 h-4 mr-2" /> Insufficient Evidence
                </span>
              )}
            </div>

            {timelineData.timeline.length > 0 ? (
              <div className="relative pl-6 sm:pl-10 space-y-12 before:absolute before:inset-0 before:ml-6 sm:before:ml-10 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                {timelineData.timeline.map((entry: any, i: number) => (
                  <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    {/* Icon */}
                    <div className="flex items-center justify-center w-12 h-12 rounded-full border-[6px] border-slate-50 bg-blue-600 shadow-md shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 absolute -left-6 md:static z-10">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                    
                    {/* Card */}
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] bg-white/60 backdrop-blur-sm border border-white/80 p-6 rounded-2xl shadow-lg hover:shadow-xl hover:border-blue-200 transition-all">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-slate-800 flex items-center text-lg">
                          <Camera className="w-5 h-5 mr-2 text-slate-500" />
                          {entry.camera_name}
                        </h3>
                        <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1.5 rounded-lg border border-emerald-200 shadow-sm">
                          {Math.round(entry.confidence * 100)}% Match
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-3 text-sm font-medium text-slate-600 bg-white/50 p-3 rounded-xl border border-white/60 w-fit">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span>{new Date(entry.first_seen).toLocaleTimeString()}</span>
                        <ChevronRight className="w-4 h-4 text-slate-300" />
                        <span>{new Date(entry.last_seen).toLocaleTimeString()}</span>
                      </div>
                      
                      <button className="mt-5 w-full bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-sm hover:shadow text-xs font-bold tracking-wider py-3 rounded-xl transition-all flex items-center justify-center">
                        <Activity className="w-4 h-4 mr-2" />
                        VIEW EVIDENCE
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 bg-white/30 rounded-2xl border border-white/50 border-dashed">
                <Clock className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                <p className="text-lg font-medium">No timeline events found for this track ID.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

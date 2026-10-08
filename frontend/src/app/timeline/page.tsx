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
    <div className="p-6 lg:p-10 max-w-5xl mx-auto w-full space-y-8 animate-in fade-in">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <Clock className="w-8 h-8 mr-3 text-blue-500" />
          Cross-Camera Timeline
        </h1>
        <p className="text-neutral-400">Track an identified object or person chronologically across the camera network.</p>
      </div>

      <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 shadow-xl">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="relative flex-1 group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500 group-focus-within:text-blue-500 transition-colors" />
            <input 
              type="text" 
              value={globalId}
              onChange={(e) => setGlobalId(e.target.value)}
              placeholder="Enter Global Track ID (e.g., uuid...)" 
              className="w-full bg-black/50 border border-neutral-700 rounded-xl pl-12 pr-4 py-3 text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-inner"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading || !globalId.trim()}
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3 rounded-xl transition-all disabled:opacity-50 min-w-[140px]"
          >
            {loading ? "Searching..." : "Trace"}
          </button>
        </form>
        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start text-red-400">
            <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      {timelineData && (
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
          <div className="mb-8 border-b border-neutral-800 pb-6 flex justify-between items-end">
            <div>
              <p className="text-xs font-bold text-neutral-500 tracking-widest uppercase mb-1">Global Track ID</p>
              <p className="text-xl font-mono text-white break-all">{timelineData.global_identity_id}</p>
            </div>
            {timelineData.insufficient_evidence && (
              <span className="bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 px-3 py-1 rounded-full text-xs font-bold flex items-center">
                <AlertTriangle className="w-3 h-3 mr-1.5" /> Insufficient Evidence
              </span>
            )}
          </div>

          {timelineData.timeline.length > 0 ? (
            <div className="relative pl-6 sm:pl-10 space-y-12 before:absolute before:inset-0 before:ml-6 sm:before:ml-10 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-neutral-700 before:to-transparent">
              {timelineData.timeline.map((entry: any, i: number) => (
                <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  {/* Icon */}
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-neutral-900 bg-blue-600 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 absolute -left-5 md:static z-10">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                  
                  {/* Card */}
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-black/40 border border-neutral-800 p-5 rounded-xl shadow-lg hover:border-blue-500/50 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-white flex items-center">
                        <Camera className="w-4 h-4 mr-2 text-neutral-400" />
                        {entry.camera_name}
                      </h3>
                      <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded border border-emerald-400/20">
                        {Math.round(entry.confidence * 100)}% Match
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-neutral-400">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(entry.first_seen).toLocaleTimeString()}</span>
                      <ChevronRight className="w-3 h-3 text-neutral-600" />
                      <span>{new Date(entry.last_seen).toLocaleTimeString()}</span>
                    </div>
                    
                    <button className="mt-4 w-full bg-neutral-800 hover:bg-neutral-700 text-white text-xs font-medium py-2 rounded transition-colors flex items-center justify-center">
                      <Activity className="w-3 h-3 mr-2" />
                      View Evidence
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-neutral-500">
              <Clock className="w-12 h-12 mx-auto mb-4 opacity-20" />
              <p>No timeline events found for this track ID.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

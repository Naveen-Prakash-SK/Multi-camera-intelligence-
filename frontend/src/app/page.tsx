"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera, QueryResponse } from "@/types";

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Fetch cameras on mount
    api.getCameras().then(setCameras).catch(e => console.error(e));
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.query(query);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to query the system.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-neutral-950 text-neutral-100 font-sans">
      {/* HEADER */}
      <header className="border-b border-neutral-800 bg-neutral-900 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold tracking-tight">Video Intelligence</h1>
        <div className="flex space-x-4 text-sm font-medium text-neutral-400">
          <a href="/health" className="hover:text-white transition-colors">System Health</a>
          <span>Alerts</span>
          <span>Settings</span>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-10">
        
        {/* CAMERA GRID */}
        <section>
          <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4">Camera Grid</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {cameras.length > 0 ? (
              cameras.map(cam => (
                <div key={cam.id} className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex flex-col justify-between aspect-video">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-neutral-200">{cam.name}</h3>
                      <p className="text-xs text-neutral-500 font-mono">{cam.id.split('-')[0]}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`h-2 w-2 rounded-full ${cam.status === 'ONLINE' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                      <span className="text-xs font-medium">{cam.status}</span>
                    </div>
                  </div>
                  <div className="text-xs text-neutral-500 flex justify-center items-center h-full">
                    {cam.status === 'ONLINE' ? 'LIVE STREAM' : 'OFFLINE'}
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full h-32 flex items-center justify-center border border-dashed border-neutral-800 rounded-lg text-neutral-500">
                No cameras connected.
              </div>
            )}
          </div>
        </section>

        {/* SEARCH */}
        <section>
          <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4">Natural Language Search</h2>
          <form onSubmit={handleSearch} className="flex space-x-2">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Find the red car that entered the main gate..." 
              className="flex-1 bg-neutral-900 border border-neutral-700 rounded-md px-4 py-3 text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              type="submit" 
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? "Searching..." : "SEARCH"}
            </button>
          </form>
          {error && <p className="text-red-400 mt-2 text-sm">{error}</p>}
        </section>

        {/* RESULT */}
        {result && (
          <section className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
            <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4">Result</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <div className="text-lg text-neutral-200 leading-relaxed border-l-4 border-blue-500 pl-4">
                  {result.answer}
                </div>
                {result.results.length > 0 && (
                  <div className="space-y-2 mt-6">
                    <p className="text-sm text-neutral-400">Match Evidence:</p>
                    <div className="bg-neutral-950 p-4 rounded-md border border-neutral-800">
                      <p><span className="text-neutral-500">Camera:</span> {result.results[0].camera_name}</p>
                      <p><span className="text-neutral-500">Time:</span> {new Date(result.results[0].timestamp).toLocaleString()}</p>
                      <p><span className="text-neutral-500">Confidence:</span> {(result.results[0].confidence * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                )}
              </div>
              <div className="bg-black rounded-md flex items-center justify-center border border-neutral-800 aspect-video relative group cursor-pointer">
                 {result.results[0]?.evidence.thumbnail_url ? (
                   <img src={result.results[0].evidence.thumbnail_url} alt="Evidence" className="w-full h-full object-cover rounded-md opacity-80 group-hover:opacity-100 transition-opacity" />
                 ) : (
                   <span className="text-neutral-600">No Image</span>
                 )}
                 <div className="absolute inset-0 flex items-center justify-center">
                   <div className="bg-black/50 p-3 rounded-full text-white backdrop-blur-sm group-hover:scale-110 transition-transform">
                     ▶ View Evidence
                   </div>
                 </div>
              </div>
            </div>
          </section>
        )}

        {/* TIMELINE */}
        <section>
          <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4">Timeline</h2>
          <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 flex items-center space-x-4 overflow-x-auto">
             <div className="flex flex-col items-center flex-shrink-0">
               <span className="text-xs text-neutral-500 mb-2">09:14</span>
               <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
               <span className="text-sm font-medium mt-2">CAM01</span>
             </div>
             <div className="h-px bg-neutral-700 flex-1 min-w-[50px]"></div>
             <div className="flex flex-col items-center flex-shrink-0 opacity-50">
               <span className="text-xs text-neutral-500 mb-2">09:16</span>
               <div className="h-3 w-3 bg-neutral-600 rounded-full"></div>
               <span className="text-sm font-medium mt-2">CAM02</span>
             </div>
             <div className="h-px bg-neutral-700 flex-1 min-w-[50px] opacity-50"></div>
             <div className="flex flex-col items-center flex-shrink-0 opacity-50">
               <span className="text-xs text-neutral-500 mb-2">09:22</span>
               <div className="h-3 w-3 bg-neutral-600 rounded-full"></div>
               <span className="text-sm font-medium mt-2">CAM04</span>
             </div>
          </div>
        </section>

      </main>
    </div>
  );
}

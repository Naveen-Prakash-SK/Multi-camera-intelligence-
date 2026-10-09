"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Bell, Clock, Plus, Target, CheckCircle2 } from "lucide-react";

export default function AlertsPage() {
  const [queries, setQueries] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  
  const [queryInput, setQueryInput] = useState("");
  const [conditionInput, setConditionInput] = useState("person enters main gate");
  
  useEffect(() => {
    loadData();
    // Auto-refresh alerts every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const q = await api.getStandingQueries();
      setQueries(q);
      const a = await api.getAlerts();
      setAlerts(a);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput) return;
    
    try {
      await api.createStandingQuery({
        query: queryInput,
        condition: conditionInput,
        cooldown_seconds: 60
      });
      setQueryInput("");
      loadData();
    } catch (e) {
      console.error("Failed to create query", e);
      alert("Failed to create alert rule");
    }
  };

  return (
    <div className="flex flex-col flex-1 w-full relative">
      <main className="flex-1 p-6 lg:p-10 max-w-[1600px] mx-auto w-full space-y-12">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-extrabold text-slate-800">Alerts & Real-time Queries</h1>
          <p className="text-slate-500">Set up standing queries to get notified of events instantly.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Create Alert Rule */}
          <section className="glass-panel p-8 rounded-3xl h-fit">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-500" /> Create Alert Rule
            </h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-600 mb-2">Query</label>
                <input 
                  type="text" 
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  placeholder="e.g. A person enters the restricted area after 8pm" 
                  className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-200 focus:border-blue-400 focus:outline-none"
                  required
                />
              </div>
              <button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition-all"
              >
                Create Standing Query
              </button>
            </form>

            <div className="mt-10">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Active Rules</h3>
              <div className="space-y-3">
                {queries.map((q) => (
                  <div key={q.id} className="p-4 bg-white/40 border border-slate-100 rounded-2xl flex justify-between items-center">
                    <div>
                      <p className="font-bold text-slate-800">{q.query}</p>
                      <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3" /> Cooldown: {q.cooldown_seconds}s
                      </p>
                    </div>
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  </div>
                ))}
                {queries.length === 0 && (
                  <p className="text-slate-500 text-sm">No active rules.</p>
                )}
              </div>
            </div>
          </section>

          {/* Triggered Alerts */}
          <section className="glass-panel p-8 rounded-3xl h-fit">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Bell className="w-5 h-5 text-rose-500" /> Triggered Alerts
            </h2>
            <div className="space-y-4">
              {alerts.map((a) => (
                <div key={a.id} className="p-4 bg-rose-50/50 border border-rose-100 rounded-2xl shadow-sm hover:shadow-md transition-all">
                  <div className="flex justify-between items-start mb-2">
                    <p className="font-bold text-rose-900">{a.message.split('.')[0]}</p>
                    <span className="text-[10px] font-bold text-rose-500 bg-rose-100 px-2 py-1 rounded-full uppercase tracking-widest shrink-0">
                      {new Date(a.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-rose-700">{a.message}</p>
                  <div className="mt-3 flex justify-between items-center border-t border-rose-100 pt-3">
                    <p className="text-[10px] text-rose-400 font-mono tracking-wider">CAM: {a.camera_id.split('-')[0]}</p>
                    {!a.is_read && <span className="w-2 h-2 rounded-full bg-rose-500"></span>}
                  </div>
                </div>
              ))}
              {alerts.length === 0 && (
                <p className="text-slate-500 text-sm flex items-center justify-center h-40 border-2 border-dashed border-slate-200 rounded-2xl">
                  No alerts triggered yet.
                </p>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

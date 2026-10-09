"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { SystemHealth } from "@/types";
import { Activity, Database, Server, RefreshCw, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

export default function HealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const fetchHealth = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.getServicesHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch system health.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const StatusIcon = ({ status }: { status: string }) => {
    if (status.includes("ONLINE")) return <CheckCircle className="w-5 h-5 text-emerald-500" />;
    if (status.includes("DEGRADED")) return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  const getStatusColor = (status: string) => {
    if (status.includes("ONLINE")) return "text-emerald-400 border-emerald-500/20 bg-emerald-500/10";
    if (status.includes("DEGRADED")) return "text-yellow-400 border-yellow-500/20 bg-yellow-500/10";
    return "text-red-400 border-red-500/20 bg-red-500/10";
  };

  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto w-full space-y-8 animate-in fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">System Health</h1>
          <p className="text-slate-500">Real-time status of backend services and intelligence models.</p>
        </div>
        <button 
          onClick={fetchHealth} 
          disabled={loading}
          className="flex items-center space-x-2 bg-white/60 border border-white/80 hover:bg-white text-slate-700 px-4 py-2 rounded-lg transition-all shadow-sm font-bold"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start text-red-600 shadow-sm">
          <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {health ? (
        <div className="space-y-8 relative">
          <div className="absolute inset-0 bg-blue-300/10 blur-[100px] rounded-full pointer-events-none -z-10"></div>
          {/* CORE API */}
          <section>
            <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase mb-4 flex items-center">
              <Activity className="w-4 h-4 mr-2" /> Gateway
            </h2>
            <div className="glass-panel rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between shadow-xl relative overflow-hidden">
              <div className="mb-4 md:mb-0">
                <p className="font-bold text-slate-800 text-lg">FastAPI Backend</p>
                <p className="text-sm text-slate-500">Main orchestration layer</p>
              </div>
              <div className={`px-4 py-2 rounded-xl border flex items-center space-x-2 shadow-sm ${getStatusColor(health.api)}`}>
                <StatusIcon status={health.api} />
                <span className="font-bold tracking-wide">{health.api}</span>
              </div>
            </div>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* SERVICES */}
            <section>
              <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase mb-4 flex items-center">
                <Database className="w-4 h-4 mr-2" /> Data & Caching
              </h2>
              <div className="glass-panel rounded-2xl overflow-hidden divide-y divide-white/50 shadow-xl">
                {Object.entries(health.services).map(([name, status]) => (
                  <div key={name} className="p-5 flex items-center justify-between bg-white/20 hover:bg-white/40 transition-colors">
                    <p className="font-bold text-slate-700 capitalize">{name}</p>
                    <div className="flex items-center space-x-3 text-sm">
                      <span className="text-slate-500 max-w-[150px] md:max-w-[200px] truncate font-medium" title={status}>
                        {status.includes(":") ? status.split(":")[1] : "OK"}
                      </span>
                      <div className={`px-2 py-1 rounded-lg border flex items-center space-x-1 shadow-sm ${getStatusColor(status)}`}>
                        <StatusIcon status={status} />
                        <span className="font-bold text-xs tracking-wide">{status.split(":")[0]}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* MODELS */}
            <section>
              <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase mb-4 flex items-center">
                <Server className="w-4 h-4 mr-2" /> Intelligence
              </h2>
              <div className="glass-panel rounded-2xl overflow-hidden divide-y divide-white/50 shadow-xl">
                {Object.entries(health.models).map(([name, status]) => (
                  <div key={name} className="p-5 flex items-center justify-between bg-white/20 hover:bg-white/40 transition-colors">
                    <p className="font-bold text-slate-700 capitalize">{name}</p>
                    <div className={`px-2 py-1 rounded-lg border flex items-center space-x-1 shadow-sm ${getStatusColor(status)}`}>
                      <StatusIcon status={status} />
                      <span className="font-bold text-xs tracking-wide">{status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-24 bg-white/40 rounded-2xl animate-pulse"></div>
          <div className="h-64 bg-white/40 rounded-2xl animate-pulse"></div>
          <div className="h-64 bg-white/40 rounded-2xl animate-pulse"></div>
        </div>
      ) : (
        <div className="p-12 text-center text-slate-500 bg-white/30 border border-white/50 border-dashed rounded-2xl">
          Could not load health data.
        </div>
      )}
    </div>
  );
}

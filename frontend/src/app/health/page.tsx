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
          <h1 className="text-3xl font-bold text-white mb-2">System Health</h1>
          <p className="text-neutral-400">Real-time status of backend services and intelligence models.</p>
        </div>
        <button 
          onClick={fetchHealth} 
          disabled={loading}
          className="flex items-center space-x-2 bg-neutral-900 border border-neutral-700 hover:bg-neutral-800 text-white px-4 py-2 rounded-lg transition-all"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start text-red-400">
          <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {health ? (
        <div className="space-y-8">
          {/* CORE API */}
          <section>
            <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4 flex items-center">
              <Activity className="w-4 h-4 mr-2" /> Gateway
            </h2>
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 flex items-center justify-between">
              <div>
                <p className="font-medium text-white text-lg">FastAPI Backend</p>
                <p className="text-sm text-neutral-400">Main orchestration layer</p>
              </div>
              <div className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${getStatusColor(health.api)}`}>
                <StatusIcon status={health.api} />
                <span className="font-bold tracking-wide">{health.api}</span>
              </div>
            </div>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* SERVICES */}
            <section>
              <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4 flex items-center">
                <Database className="w-4 h-4 mr-2" /> Data & Caching
              </h2>
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden divide-y divide-neutral-800">
                {Object.entries(health.services).map(([name, status]) => (
                  <div key={name} className="p-4 flex items-center justify-between">
                    <p className="font-medium text-white capitalize">{name}</p>
                    <div className="flex items-center space-x-3 text-sm">
                      <span className="text-neutral-400 max-w-[200px] truncate" title={status}>
                        {status.includes(":") ? status.split(":")[1] : "OK"}
                      </span>
                      <div className={`px-2 py-1 rounded border flex items-center space-x-1 ${getStatusColor(status)}`}>
                        <StatusIcon status={status} />
                        <span className="font-semibold text-xs tracking-wide">{status.split(":")[0]}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* MODELS */}
            <section>
              <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-4 flex items-center">
                <Server className="w-4 h-4 mr-2" /> Intelligence
              </h2>
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden divide-y divide-neutral-800">
                {Object.entries(health.models).map(([name, status]) => (
                  <div key={name} className="p-4 flex items-center justify-between">
                    <p className="font-medium text-white capitalize">{name}</p>
                    <div className={`px-2 py-1 rounded border flex items-center space-x-1 ${getStatusColor(status)}`}>
                      <StatusIcon status={status} />
                      <span className="font-semibold text-xs tracking-wide">{status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-24 bg-neutral-900 rounded-xl animate-pulse"></div>
          <div className="h-64 bg-neutral-900 rounded-xl animate-pulse"></div>
          <div className="h-64 bg-neutral-900 rounded-xl animate-pulse"></div>
        </div>
      ) : (
        <div className="p-12 text-center text-neutral-500 border border-neutral-800 border-dashed rounded-xl">
          Could not load health data.
        </div>
      )}
    </div>
  );
}

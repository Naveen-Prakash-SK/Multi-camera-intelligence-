"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { SystemHealth } from "@/types";

export default function HealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getServicesHealth()
      .then(setHealth)
      .catch((e) => setError(e.message || "Failed to load system health"))
      .finally(() => setLoading(false));
  }, []);

  const StatusDot = ({ status }: { status: string }) => (
    <span className={`inline-block h-3 w-3 rounded-full mr-3 ${status === 'ONLINE' ? 'bg-emerald-500' : status === 'DEGRADED' ? 'bg-amber-500' : 'bg-red-500'}`} />
  );

  return (
    <div className="flex flex-col min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      <div className="max-w-4xl mx-auto w-full">
        <h1 className="text-2xl font-bold tracking-tight mb-8">System Health</h1>
        
        {loading ? (
          <p className="text-neutral-500">Loading system status...</p>
        ) : error ? (
          <div className="bg-red-950/30 border border-red-900 rounded-lg p-6">
            <h2 className="text-lg font-medium text-red-500 mb-2">Backend Connection Failed</h2>
            <p className="text-neutral-400">{error}</p>
          </div>
        ) : health ? (
          <div className="space-y-8">
            <section className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
              <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-6">Core Services</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-neutral-950 rounded border border-neutral-800">
                  <span className="font-medium">Backend API</span>
                  <div className="flex items-center"><StatusDot status={health.api} /> {health.api}</div>
                </div>
                <div className="flex items-center justify-between p-4 bg-neutral-950 rounded border border-neutral-800">
                  <span className="font-medium">PostgreSQL</span>
                  <div className="flex items-center"><StatusDot status={health.services.postgresql} /> {health.services.postgresql}</div>
                </div>
                <div className="flex items-center justify-between p-4 bg-neutral-950 rounded border border-neutral-800">
                  <span className="font-medium">Redis</span>
                  <div className="flex items-center"><StatusDot status={health.services.redis} /> {health.services.redis}</div>
                </div>
                <div className="flex items-center justify-between p-4 bg-neutral-950 rounded border border-neutral-800">
                  <span className="font-medium">Qdrant Vector DB</span>
                  <div className="flex items-center"><StatusDot status={health.services.qdrant} /> {health.services.qdrant}</div>
                </div>
              </div>
            </section>
            
            <section className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
              <h2 className="text-sm font-semibold tracking-widest text-neutral-500 uppercase mb-6">Machine Learning Models</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-neutral-950 rounded border border-neutral-800">
                  <span className="font-medium">Ollama Server (Qwen3)</span>
                  <div className="flex items-center"><StatusDot status={health.models.ollama} /> {health.models.ollama}</div>
                </div>
              </div>
            </section>
          </div>
        ) : null}
      </div>
    </div>
  );
}

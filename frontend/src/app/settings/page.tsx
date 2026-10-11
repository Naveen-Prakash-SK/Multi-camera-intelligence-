"use client";

import { Settings, Server, PlayCircle, Eye } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="p-6 lg:p-10 max-w-4xl mx-auto w-full space-y-8 animate-in fade-in relative">
      <div className="absolute inset-0 bg-blue-300/10 blur-[100px] rounded-full pointer-events-none -z-10"></div>
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2 flex items-center">
          <Settings className="w-8 h-8 mr-3 text-blue-600" />
          Settings
        </h1>
        <p className="text-slate-500">Configure dashboard preferences and application settings.</p>
      </div>

      <div className="space-y-6">
        {/* Backend Configuration */}
        <section className="glass-panel rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 border-b border-white/50 flex items-center bg-white/20">
            <Server className="w-5 h-5 text-slate-500 mr-3" />
            <h2 className="text-lg font-bold text-slate-800">Backend Connection</h2>
          </div>
          <div className="p-6">
            <label className="block text-sm font-bold text-slate-500 mb-2 tracking-wide">API Base URL</label>
            <input 
              type="text" 
              readOnly
              value={process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"} 
              className="w-full bg-white/50 border border-slate-200 rounded-xl px-4 py-3 text-slate-600 cursor-not-allowed shadow-inner focus:outline-none"
            />
            <p className="mt-2 text-xs font-medium text-slate-400">Configured via environment variables (.env)</p>
          </div>
        </section>

        {/* Playback Preferences */}
        <section className="glass-panel rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 border-b border-white/50 flex items-center bg-white/20">
            <PlayCircle className="w-5 h-5 text-slate-500 mr-3" />
            <h2 className="text-lg font-bold text-slate-800">Evidence Playback</h2>
          </div>
          <div className="p-6 space-y-4">
            <label className="flex items-center p-4 border border-white/60 bg-white/40 rounded-xl cursor-not-allowed opacity-70 shadow-sm">
              <input type="checkbox" checked readOnly className="w-4 h-4 text-blue-600 bg-white border-slate-300 rounded" />
              <div className="ml-4">
                <p className="text-sm font-bold text-slate-700">Auto-play evidence clips</p>
                <p className="text-xs font-medium text-slate-500">Automatically play video when intelligence report appears</p>
              </div>
            </label>
            <label className="flex items-center p-4 border border-white/60 bg-white/40 rounded-xl cursor-not-allowed opacity-70 shadow-sm">
              <input type="checkbox" checked readOnly className="w-4 h-4 text-blue-600 bg-white border-slate-300 rounded" />
              <div className="ml-4">
                <p className="text-sm font-bold text-slate-700">Show detection bounding boxes</p>
                <p className="text-xs font-medium text-slate-500">Overlay Spatial IoU tracking boxes on evidence playback</p>
              </div>
            </label>
          </div>
        </section>

        {/* UI Preferences */}
        <section className="glass-panel rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 border-b border-white/50 flex items-center bg-white/20">
            <Eye className="w-5 h-5 text-slate-500 mr-3" />
            <h2 className="text-lg font-bold text-slate-800">Appearance</h2>
          </div>
          <div className="p-6">
            <div className="flex space-x-4">
              <div className="border-2 border-blue-400 rounded-xl overflow-hidden cursor-not-allowed w-32 relative shadow-md">
                <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px] flex items-center justify-center border border-white/50">
                  <span className="bg-white px-2 py-1 rounded-lg text-xs text-blue-700 font-bold shadow-sm">Glass Theme</span>
                </div>
                <div className="h-4 bg-slate-100"></div>
                <div className="h-16 bg-slate-50 flex flex-col p-2 space-y-1">
                  <div className="h-2 w-3/4 bg-slate-200 rounded"></div>
                  <div className="h-6 w-full bg-slate-200 rounded"></div>
                </div>
              </div>
            </div>
            <p className="mt-4 text-xs font-medium text-slate-500 leading-relaxed">
              The intelligence dashboard uses a strictly enforced pleasant glassmorphism theme optimized for modern CCTV monitoring environments.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

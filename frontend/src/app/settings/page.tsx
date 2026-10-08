"use client";

import { Settings, Server, PlayCircle, Eye } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="p-6 lg:p-10 max-w-4xl mx-auto w-full space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
          <Settings className="w-8 h-8 mr-3 text-blue-500" />
          Settings
        </h1>
        <p className="text-neutral-400">Configure dashboard preferences and application settings.</p>
      </div>

      <div className="space-y-6">
        {/* Backend Configuration */}
        <section className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-neutral-800 flex items-center">
            <Server className="w-5 h-5 text-neutral-400 mr-3" />
            <h2 className="text-lg font-medium text-white">Backend Connection</h2>
          </div>
          <div className="p-6">
            <label className="block text-sm font-medium text-neutral-400 mb-2">API Base URL</label>
            <input 
              type="text" 
              readOnly
              value={process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"} 
              className="w-full bg-black/50 border border-neutral-700 rounded-lg px-4 py-3 text-neutral-500 cursor-not-allowed"
            />
            <p className="mt-2 text-xs text-neutral-500">Configured via environment variables (.env)</p>
          </div>
        </section>

        {/* Playback Preferences */}
        <section className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-neutral-800 flex items-center">
            <PlayCircle className="w-5 h-5 text-neutral-400 mr-3" />
            <h2 className="text-lg font-medium text-white">Evidence Playback</h2>
          </div>
          <div className="p-6 space-y-4">
            <label className="flex items-center p-4 border border-neutral-800 rounded-xl cursor-not-allowed opacity-70">
              <input type="checkbox" checked readOnly className="w-4 h-4 text-blue-600 bg-neutral-900 border-neutral-700" />
              <div className="ml-4">
                <p className="text-sm font-medium text-white">Auto-play evidence clips</p>
                <p className="text-xs text-neutral-500">Automatically play video when intelligence report appears</p>
              </div>
            </label>
            <label className="flex items-center p-4 border border-neutral-800 rounded-xl cursor-not-allowed opacity-70">
              <input type="checkbox" checked readOnly className="w-4 h-4 text-blue-600 bg-neutral-900 border-neutral-700" />
              <div className="ml-4">
                <p className="text-sm font-medium text-white">Show detection bounding boxes</p>
                <p className="text-xs text-neutral-500">Overlay Spatial IoU tracking boxes on evidence playback</p>
              </div>
            </label>
          </div>
        </section>

        {/* UI Preferences */}
        <section className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-neutral-800 flex items-center">
            <Eye className="w-5 h-5 text-neutral-400 mr-3" />
            <h2 className="text-lg font-medium text-white">Appearance</h2>
          </div>
          <div className="p-6">
            <div className="flex space-x-4">
              <div className="border-2 border-blue-500 rounded-xl overflow-hidden cursor-not-allowed w-32 relative">
                <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
                  <span className="bg-black/80 px-2 py-1 rounded text-xs text-white font-medium">Dark Mode</span>
                </div>
                <div className="h-4 bg-neutral-900"></div>
                <div className="h-16 bg-neutral-950 flex flex-col p-2 space-y-1">
                  <div className="h-2 w-3/4 bg-neutral-800 rounded"></div>
                  <div className="h-6 w-full bg-neutral-800 rounded"></div>
                </div>
              </div>
            </div>
            <p className="mt-4 text-xs text-neutral-500">The intelligence dashboard uses a strictly enforced high-contrast dark theme optimized for CCTV monitoring environments.</p>
          </div>
        </section>
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api/client";
import { Camera, ProcessingJob } from "@/types";
import { Upload, FileVideo, HardDrive, RefreshCw, AlertTriangle, CheckCircle, Clock } from "lucide-react";

export default function FootagePage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<ProcessingJob | null>(null);

  useEffect(() => {
    api.getCameras().then(setCameras).catch(e => console.error("Failed to load cameras", e));
  }, []);

  // Poll job status
  useEffect(() => {
    if (!activeJobId) return;
    
    const interval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(activeJobId);
        setJobStatus(job);
        
        if (job.status === "COMPLETED" || job.status === "FAILED") {
          clearInterval(interval);
          setUploading(false);
        }
      } catch (e) {
        console.error(e);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [activeJobId]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedCamera) return;
    
    setUploading(true);
    setError("");
    setJobStatus(null);
    
    try {
      const res = await api.uploadFootage(file, selectedCamera, new Date().toISOString());
      setActiveJobId(res.job_id);
    } catch (err: any) {
      setError(err.message || "Failed to upload footage.");
      setUploading(false);
    }
  };

  const getJobProgress = () => {
    if (!jobStatus) return 0;
    return jobStatus.progress;
  };

  return (
    <div className="p-6 lg:p-10 max-w-4xl mx-auto w-full space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2 flex items-center">
          <HardDrive className="w-8 h-8 mr-3 text-blue-600" />
          Footage Ingestion
        </h1>
        <p className="text-slate-500">Upload recorded CCTV footage into the intelligence processing pipeline.</p>
      </div>

      <div className="glass-panel rounded-[2rem] p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-blue-300/10 blur-[50px] rounded-full pointer-events-none"></div>
        <form onSubmit={handleUpload} className="space-y-6 relative z-10">
          <div>
            <label className="block text-sm font-bold text-slate-600 mb-2">Target Camera / Location</label>
            <select 
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
              disabled={uploading}
              className="w-full bg-white/60 backdrop-blur-md border border-white/80 rounded-2xl px-4 py-4 text-slate-800 focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all text-lg shadow-inner disabled:opacity-50"
            >
              <option value="">Select a camera source...</option>
              {cameras.map(cam => (
                <option key={cam.id} value={cam.id}>{cam.name} ({cam.location})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-600 mb-2">Video File (.mp4, .mkv, .avi)</label>
            <div className="mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-slate-300 border-dashed rounded-2xl hover:border-blue-400 transition-colors bg-white/40 shadow-sm">
              <div className="space-y-2 text-center">
                <FileVideo className="mx-auto h-12 w-12 text-slate-400" />
                <div className="flex text-sm text-slate-600 justify-center">
                  <label className="relative cursor-pointer rounded-md font-bold text-blue-600 hover:text-blue-500 focus-within:outline-none">
                    <span>Upload a file</span>
                    <input 
                      type="file" 
                      accept="video/mp4,video/x-mkv,video/avi" 
                      className="sr-only" 
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      disabled={uploading}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-slate-500 font-medium">
                  {file ? file.name : "No file selected"}
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start text-red-600 shadow-sm">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          <button 
            type="submit" 
            disabled={uploading || !file || !selectedCamera}
            className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold px-8 py-4 rounded-xl transition-all disabled:opacity-50 shadow-lg hover:shadow-blue-500/25"
          >
            {uploading && !activeJobId ? (
              <RefreshCw className="w-5 h-5 animate-spin mr-2" />
            ) : (
              <Upload className="w-5 h-5 mr-2" />
            )}
            {uploading && !activeJobId ? "Uploading..." : "Process Footage"}
          </button>
        </form>
      </div>

      {/* JOB TRACKER */}
      {activeJobId && (
        <div className="glass-panel rounded-2xl p-8 shadow-xl animate-in slide-in-from-bottom-4">
          <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center">
            Pipeline Status
            {jobStatus?.status === 'COMPLETED' && <CheckCircle className="ml-2 w-5 h-5 text-emerald-500" />}
            {jobStatus?.status === 'FAILED' && <AlertTriangle className="ml-2 w-5 h-5 text-rose-500" />}
          </h2>
          
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500 font-bold tracking-wide uppercase text-xs">State: <span className="text-slate-800 ml-1">{jobStatus?.status || 'QUEUED'}</span></span>
              <span className="text-slate-500 font-bold tracking-wide uppercase text-xs">Progress: <span className="text-blue-600 ml-1">{getJobProgress().toFixed(0)}%</span></span>
            </div>
            
            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden border border-slate-200 inset-shadow-sm">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ${jobStatus?.status === 'FAILED' ? 'bg-rose-500' : jobStatus?.status === 'COMPLETED' ? 'bg-emerald-500' : 'bg-blue-500'}`}
                style={{ width: `${getJobProgress()}%` }}
              ></div>
            </div>
            
            {jobStatus?.error && (
              <div className="mt-4 text-sm text-rose-700 bg-rose-50 p-3 rounded-lg border border-rose-200">
                {jobStatus.error}
              </div>
            )}
            
            <div className="flex items-center text-xs text-slate-400 font-medium space-x-4 mt-6 border-t border-white/50 pt-4">
              <div className="flex items-center"><Clock className="w-4 h-4 mr-1 text-slate-300" /> Job ID: {activeJobId.split('-')[0]}...</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

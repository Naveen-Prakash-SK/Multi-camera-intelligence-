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
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
          <HardDrive className="w-8 h-8 mr-3 text-blue-500" />
          Footage Ingestion
        </h1>
        <p className="text-neutral-400">Upload recorded CCTV footage into the intelligence processing pipeline.</p>
      </div>

      <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-xl">
        <form onSubmit={handleUpload} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Target Camera / Location</label>
            <select 
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
              disabled={uploading}
              className="w-full bg-black/50 border border-neutral-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            >
              <option value="">Select a camera source...</option>
              {cameras.map(cam => (
                <option key={cam.id} value={cam.id}>{cam.name} ({cam.location})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Video File (.mp4, .mkv, .avi)</label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-neutral-700 border-dashed rounded-xl hover:border-blue-500/50 transition-colors bg-black/20">
              <div className="space-y-2 text-center">
                <FileVideo className="mx-auto h-12 w-12 text-neutral-500" />
                <div className="flex text-sm text-neutral-400 justify-center">
                  <label className="relative cursor-pointer rounded-md font-medium text-blue-500 hover:text-blue-400 focus-within:outline-none">
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
                <p className="text-xs text-neutral-500">
                  {file ? file.name : "No file selected"}
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start text-red-400">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          <button 
            type="submit" 
            disabled={uploading || !file || !selectedCamera}
            className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-4 rounded-xl transition-all disabled:opacity-50 shadow-lg"
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
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-2xl animate-in slide-in-from-bottom-4">
          <h2 className="text-lg font-bold text-white mb-6 flex items-center">
            Pipeline Status
            {jobStatus?.status === 'COMPLETED' && <CheckCircle className="ml-2 w-5 h-5 text-emerald-500" />}
            {jobStatus?.status === 'FAILED' && <AlertTriangle className="ml-2 w-5 h-5 text-red-500" />}
          </h2>
          
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-neutral-400 font-medium">State: <span className="text-white ml-1">{jobStatus?.status || 'QUEUED'}</span></span>
              <span className="text-neutral-400 font-medium">Progress: <span className="text-white ml-1">{getJobProgress().toFixed(0)}%</span></span>
            </div>
            
            <div className="w-full bg-black rounded-full h-3 overflow-hidden border border-neutral-800">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ${jobStatus?.status === 'FAILED' ? 'bg-red-500' : jobStatus?.status === 'COMPLETED' ? 'bg-emerald-500' : 'bg-blue-500'}`}
                style={{ width: `${getJobProgress()}%` }}
              ></div>
            </div>
            
            {jobStatus?.error && (
              <div className="mt-4 text-sm text-red-400 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                {jobStatus.error}
              </div>
            )}
            
            <div className="flex items-center text-xs text-neutral-500 space-x-4 mt-6">
              <div className="flex items-center"><Clock className="w-3 h-3 mr-1" /> Job ID: {activeJobId.split('-')[0]}...</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

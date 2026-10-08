export interface Gateway {
  id: string;
  name: string;
  status: "ONLINE" | "OFFLINE";
}

export interface Camera {
  id: string;
  name: string;
  gateway_id?: string;
  stream_url?: string;
  status: "ONLINE" | "OFFLINE" | "ERROR" | "CONNECTING";
  clock_offset_ms: number;
  location?: string;
  description?: string;
}

export interface VideoFile {
  id: string;
  camera_id: string;
  capture_start_utc: string;
  provenance: string;
  file_path: string;
  codec?: string;
  fps?: number;
  duration_s?: number;
}

export interface ProcessingJob {
  id: string;
  job_type: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface SceneMemory {
  id: string;
  location_name: string;
  camera_id: string;
  zone_id?: string;
  aliases: string[];
  version: number;
}

export interface Event {
  id: string;
  camera_id: string;
  timestamp_start: string;
  timestamp_end?: string;
  event_type: string;
  track_id?: string;
  global_identity_id?: string;
  object_type: string;
  attributes?: Record<string, any>;
  zone_id?: string;
  confidence: number;
  frame_ref?: string;
  clip_ref?: string;
}

export interface EvidenceRef {
  evidence_id: string;
  thumbnail_url: string;
  clip_url: string;
}

export interface QueryResultItem {
  event_id: string;
  camera_id: string;
  camera_name: string;
  timestamp: string;
  object_type: string;
  attributes: Record<string, any>;
  confidence: number;
  verification: Record<string, string>;
  evidence: EvidenceRef;
}

export interface QueryResponse {
  verdict: string;
  answer: string;
  grounded: boolean;
  resolved: Record<string, any>;
  coverage: Record<string, any>;
  results: QueryResultItem[];
  trace_id: string;
  confidence: number;
}

export interface SystemHealth {
  api: string;
  services: {
    postgresql: string;
    redis: string;
    qdrant: string;
  };
  models: {
    ollama: string;
  };
}

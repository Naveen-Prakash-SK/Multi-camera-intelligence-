import { Camera, SceneMemory, QueryResponse, SystemHealth, ProcessingJob } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Ignore json parse error for non-json responses
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  private async requestFormData<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch { }
        throw new Error(errorMessage);
      }
      return response.json();
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  // Health
  async getHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/api/health");
  }

  async getServicesHealth(): Promise<SystemHealth> {
    return this.request<SystemHealth>("/api/health/services");
  }

  // Cameras
  async getCameras(): Promise<Camera[]> {
    return this.request<Camera[]>("/api/cameras");
  }

  async getCamera(id: string): Promise<Camera> {
    return this.request<Camera>(`/api/cameras/${id}`);
  }

  async createCamera(camera: Partial<Camera>): Promise<Camera> {
    return this.request<Camera>("/api/cameras", {
      method: "POST",
      body: JSON.stringify(camera),
    });
  }

  async updateCamera(id: string, camera: Partial<Camera>): Promise<Camera> {
    return this.request<Camera>(`/api/cameras/${id}`, {
      method: "PUT",
      body: JSON.stringify(camera),
    });
  }

  async deleteCamera(id: string): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/api/cameras/${id}`, {
      method: "DELETE",
    });
  }

  async startCamera(id: string): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/api/cameras/${id}/start`, { method: "POST" });
  }

  async stopCamera(id: string): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/api/cameras/${id}/stop`, { method: "POST" });
  }

  // Footage Upload
  async uploadFootage(file: File, cameraId: string, captureStartUtc: string): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("camera_id", cameraId);
    formData.append("capture_start_utc", captureStartUtc);
    return this.requestFormData("/api/footage", formData);
  }

  async getJobStatus(id: string): Promise<ProcessingJob> {
    return this.request<ProcessingJob>(`/api/jobs/${id}`);
  }

  // Scene Memory
  async getSceneMemory(): Promise<SceneMemory[]> {
    return this.request<SceneMemory[]>("/api/memory");
  }

  async createSceneMemory(data: Partial<SceneMemory>): Promise<SceneMemory> {
    return this.request<SceneMemory>("/api/memory", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Timeline
  async getTimeline(globalIdentityId: string): Promise<any> {
    return this.request<any>(`/api/timeline/${globalIdentityId}`);
  }

  async query(query: string, sessionId?: string, clarificationAnswer?: any): Promise<QueryResponse> {
    return this.request<QueryResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify({ 
        query, 
        session_id: sessionId,
        clarification_answer: clarificationAnswer
      }),
    });
  }
}

export const api = new ApiClient();

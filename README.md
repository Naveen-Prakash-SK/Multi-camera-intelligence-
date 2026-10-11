# Multi-Camera Intelligence Platform

**"Ask your cameras what happened."**

## Problem Statement
**HNX26EPS05 — Multi-Stream Video Intelligence with Conversational Query.**
This system accepts multiple CCTV video streams and recorded footage, detects and indexes events across cameras, and provides a conversational intelligence interface where users can ask natural-language questions (e.g., *"Did a red car pass through the main gate?"*, *"Was there a person carrying a bag in the lobby?"*).

---

## System Architecture

The application is built using a containerized microservices architecture:

- **Frontend:** Next.js (React), Tailwind CSS, Lucide Icons
- **Backend:** FastAPI (Python), SQLAlchemy, asyncpg
- **Worker:** Celery (configured with `-P solo` for stable AI model inference)
- **Computer Vision & ML:** OpenCV, FFmpeg, Ultralytics YOLO, SigLIP (OpenCLIP), Transformers
- **Databases & Caching:** 
  - **PostgreSQL**: Primary application state, metadata, and relations
  - **Redis**: Celery broker and MJPEG frame buffer
  - **Qdrant**: Vector database for dense semantic search
  - **SQLite**: Local caching & MVP lightweight persistence

---

## Core Features

- **Live Camera Streaming:** Ingest RTSP/HTTP streams via FFmpeg, process frames in real-time (object detection, privacy blurring), and serve MJPEG streams directly to the dashboard.
- **Video File Analysis:** Upload or process recorded CCTV footage for asynchronous frame-by-frame analysis and embedding generation.
- **Semantic & Natural Language Search:** Search through video events using natural language queries with similarity scoring and grounded evidence.
- **Visual Evidence Grounding:** Responses return the exact camera, timestamp, confidence score, and visual evidence frames/clips.
- **Clarify-Once Memory:** Disambiguates conversational location references (e.g. mapping "main gate" to specific cameras) and persists the mapping for future queries.
- **Privacy Enforcement:** Automatic detection and blurring of sensitive objects (e.g., faces, license plates).
- **Standing Queries & Alerts:** Define persistent queries that trigger alerts when specific events are detected in the video stream.

---

## Prerequisites

- Python 3.10+ / Node.js 18+
- Docker and Docker Compose
- (Optional) NVIDIA GPU with Docker support for accelerated inference

---

## Quick Start (Docker Compose - Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Naveen-Prakash-SK/Multi-camera-intelligence-.git
   cd Multi-camera-intelligence-
   ```

2. **Start all services with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```
   This spins up: `postgres`, `redis`, `qdrant`, `backend`, `celery_worker`, and `frontend`.

3. **Access the Application:**
   - **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Default Credentials
- **Email:** `admin@gmail.com`
- **Password:** `passs123456`

---

## Standalone Local Setup

### 1. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# Run migrations / initialization
python seed_db.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

---

## Demo Dataset & Video Processing

Sample CCTV videos and metadata are included in `backend/data/`:
- `camera_01.mp4`, `camera_02.mp4`, `camera_03.mp4`
- `cameras.json`, `demo_queries.json`, `dataset_metadata.json`

To register cameras and run batch processing scripts:
```powershell
cd backend
python init_demo_data.py
python process_all_and_verify.py
```

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (auth, cameras, footage, memory, query, evidence)
│   │   ├── core/         # Settings, configuration, security
│   │   ├── models/       # SQLAlchemy models and schemas
│   │   ├── providers/    # LLM and inference interfaces (Ollama, CLIP, SigLIP)
│   │   ├── services/     # Indexer, video processing services
│   │   ├── vector/       # Qdrant client, embeddings, ReID, detection
│   │   └── workers/      # Celery task definitions, tracking, frame source
│   ├── data/             # Demo CCTV footage (.mp4) and metadata
│   ├── scripts/          # Dataset setup and download utilities
│   ├── storage/          # Local frame and database storage
│   ├── Dockerfile
│   └── main.py           # Backend application entry point
├── frontend/
│   ├── src/app/          # Next.js App Router (dashboard, cameras, footage, alerts, timeline)
│   ├── src/components/   # Reusable UI components & video players
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml     # Multi-container orchestration
```

---

## Known Technical Notes

- **Celery Worker Execution:** Celery is run with `-P solo` to prevent multiprocessing/fork issues during Torch and CUDA model initialization.
- **Database Connection Pooling:** The backend utilizes `NullPool` for async PostgreSQL connections to prevent deadlocks and connection exhaustion.
- **Live Stream Auth Bypass:** MJPEG stream endpoints (`/api/cameras/.../stream/raw` and `/processed`) bypass JWT authentication for direct browser video compatibility.

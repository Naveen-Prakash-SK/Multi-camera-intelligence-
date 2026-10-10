# Multi-Camera Intelligence Platform

A comprehensive, full-stack video intelligence platform that ingests live camera streams or recorded footage, processes them using advanced computer vision models (YOLO, SigLIP), and provides semantic search, alerting, and live monitoring via a modern web dashboard.

## System Architecture

The application is built using a containerized microservices architecture:

- **Frontend:** Next.js (React), Tailwind CSS, Lucide Icons
- **Backend:** FastAPI (Python), SQLAlchemy, asyncpg
- **Worker:** Celery (configured with `-P solo` for stable AI model inference)
- **Computer Vision:** OpenCV, FFmpeg, Ultralytics YOLO, SigLIP (OpenCLIP)
- **Databases & Caching:** 
  - PostgreSQL (Primary application state)
  - Redis (Celery broker, MJPEG frame buffer)
  - Qdrant (Vector database for semantic search)

## Features

- **Live Camera Streaming:** Ingest RTSP/HTTP streams via FFmpeg, process frames in real-time (object detection, privacy blurring), and serve MJPEG streams directly to the dashboard.
- **Video File Analysis:** Upload recorded footage for asynchronous frame-by-frame analysis and embedding generation.
- **Semantic Search:** Search through video events using natural language (e.g., "red car near the gate").
- **Privacy Enforcement:** Automatic detection and blurring of sensitive objects (e.g., faces, license plates).
- **Standing Queries & Alerts:** Define persistent queries that trigger alerts when specific events are detected in the video stream.

## Prerequisites

- Docker and Docker Compose
- (Optional) NVIDIA GPU with Docker support for accelerated inference

## Getting Started

1. **Clone the repository**
2. **Start the application using Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```
   This will spin up all required services: `postgres`, `redis`, `qdrant`, `backend`, `celery_worker`, and `frontend`.

3. **Access the Application:**
   - **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Default Credentials

The platform is secured with JWT authentication. Use the following credentials to access the dashboard:

- **Email:** `admin@gmail.com`
- **Password:** `passs123456`

## Known Technical Constraints

- **Celery Worker Execution:** Due to the complexities of `fork()` and CUDA/Torch initialization in multiprocessing environments, the Celery worker is deliberately run with `-P solo`.
- **Database Connection Pooling:** The backend utilizes `NullPool` for PostgreSQL connections to prevent deadlocks and connection exhaustion in the async context.
- **Live Stream Auth Bypass:** For stability and browser compatibility, MJPEG stream endpoints (`/api/cameras/.../stream/raw` and `/processed`) bypass JWT authentication in the middleware, relying on network-level access control.

## Project Structure

- `/frontend` - Next.js client application
- `/backend` - FastAPI server, Celery worker definitions, and ML pipelines
- `/backend/app/api` - REST endpoints
- `/backend/app/vector` - Vector database integration and Advanced AI Pipeline
- `/docker-compose.yml` - Container orchestration

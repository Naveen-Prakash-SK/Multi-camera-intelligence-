# Multi-camera-intelligence-

**"Ask your cameras what happened."**

## Problem Statement
HNX26EPS05 — Multi-Stream Video Intelligence with Conversational Query.
This system accepts multiple recorded CCTV streams/videos, detects/indexes events across cameras, and provides a conversational interface where users can ask natural-language questions (e.g. "Did a red car pass through the main gate?").

## MVP Features
1. **Multi-Camera Input**: Supports processing of multiple `.mp4` video files representing different CCTV cameras.
2. **Video Processing & Indexing**: Extracts frames from videos, classifies events using a zero-shot vision-language model (CLIP), and indexes embeddings for semantic search.
3. **Conversational Search**: Search across multiple cameras using natural language.
4. **Grounded Responses**: Results return exact camera, timestamp, and visual evidence (frames).
5. **Clarify-Once Memory**: If the system doesn't know what "main gate" refers to, it asks the user to clarify which camera, and remembers the mapping for future queries.
6. **Dark Professional UI**: A clean, security-focused web dashboard built with React.

## Architecture & Tech Stack
- **Frontend**: React (Vite) + Vanilla CSS + Lucide Icons.
- **Backend**: Python + FastAPI.
- **Computer Vision**: OpenCV (frame extraction), HuggingFace Transformers (CLIP model for zero-shot image embeddings and classification).
- **Database/Vector Store**: SQLite for metadata, events, and clarify-once memory; Numpy cosine similarity for lightweight vector search.

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup
```powershell
cd frontend
npm install
```

## How to Add CCTV Videos (Demo Data)

To test the system, you must provide some sample `.mp4` videos.

1. Place your CCTV video files in the `backend/data/` directory (create the directory if it doesn't exist).
2. Start the backend.
3. Run the initial data script to register the demo cameras in the database:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python init_demo_data.py
   ```
4. Process the videos (this will extract frames and index them). You can do this via an API tool (e.g. Postman, cURL) or a simple Python script.
   
   Example processing request:
   ```powershell
   curl -X POST "http://localhost:8000/api/process" -H "Content-Type: application/json" -d '{"camera_id": "camera_01", "video_path": "data/camera_01.mp4"}'
   ```
   *Repeat this for `camera_02.mp4` and `camera_03.mp4` with their respective `camera_id`s.*

## Starting the Application

### Start Backend
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```powershell
cd frontend
npm run dev
```
Then navigate to `http://localhost:5173`.

## Demo Flow

1. Open the UI.
2. Go to the **Cameras** page to verify the cameras are online.
3. Go to **Ask Cameras** (Dashboard) and ask a query:
   - *"Did a red car enter the main gate?"*
   - *"Was there a person carrying a bag in the lobby?"*
4. The system will retrieve the matching camera, timestamp, and display the evidence frame.
5. **Clarify-Once Demo**:
   - Ask: *"Did anyone enter the main gate?"*
   - If the system doesn't know "main gate", a clarification card will appear.
   - Select the correct camera (e.g., "Camera 01 - Main Gate").
   - The query will automatically re-run.
   - Restart the backend and ask again to verify it remembers.

## Known Limitations (Hackathon MVP)
- CLIP model runs on CPU by default which can be slow for long videos.
- Video clips are not fully extracted for evidence; the MVP uses the keyframe image instead.
- Simple cosine similarity over numpy arrays is used instead of a dedicated vector DB (e.g., FAISS) to eliminate complex dependencies.

## Future Extensions
- Integrate FAISS for large-scale vector search.
- Use FFmpeg to dynamically serve trimmed `.mp4` evidence clips instead of static frames.
- Add live RTSP streaming support.
- Improve entity extraction using an LLM to parse natural language queries better.

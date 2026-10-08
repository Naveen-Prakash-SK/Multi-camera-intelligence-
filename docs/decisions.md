# Architectural Decisions

This document records the major design and architecture decisions for the Multi-Camera Video-Intelligence Backend.

## 1. Core Framework
- **Decision**: Python 3.12+ with FastAPI.
- **Alternatives Considered**: Node.js with Express or NestJS.
- **Reason**: Python is the lingua franca of machine learning. Since we are integrating heavily with CV models (YOLO, SigLIP, OSNet, etc.) and LLMs (Ollama/Qwen3), a Python backend avoids unnecessary HTTP overhead and complexity for ML bindings, making direct in-process integrations feasible for workers. FastAPI provides the necessary async performance and Pydantic validation out of the box.

## 2. Dependency Management
- **Decision**: `uv`.
- **Alternatives Considered**: `poetry`, standard `pip`.
- **Reason**: `uv` is extremely fast and robust for resolving dependencies and managing virtual environments, which is highly beneficial for Python projects with heavy ML dependencies.

## 3. Database ORM
- **Decision**: SQLAlchemy 2.0 + Alembic.
- **Alternatives Considered**: SQLModel, Prisma for Python.
- **Reason**: SQLAlchemy is the industry standard for Python ORMs. It offers maximum flexibility for complex schemas (like our spatial zones, topologies, and heavily normalized event tables) and robust migration support via Alembic.

## 4. Background Workers
- **Decision**: Celery + Redis.
- **Alternatives Considered**: RQ (Redis Queue), ARQ.
- **Reason**: Video processing requires robust retry mechanisms, complex workflows (e.g. chaining detection → tracking → embedding), and solid monitoring. Celery is the most robust and mature solution for this in the Python ecosystem.

## 5. Model Inference Architecture
- **Decision**: Abstract Provider interfaces (`ObjectDetectionProvider`, `TextEmbeddingProvider`, etc.).
  - Ollama models (Qwen3) run externally over HTTP.
  - CV models (YOLO, SigLIP, BGE-M3, OSNet) run locally in-process within the Celery workers.
- **Alternatives Considered**: Dedicated Model Server Microservice for all models, Mocking inference.
- **Reason**: Running CV models directly in the worker environment reduces network serialization overhead for video frames and minimizes microservice sprawl for this MVP. Abstracting behind a provider interface ensures they can easily be extracted into a dedicated Model Server later without affecting the orchestration logic. Mocking was explicitly forbidden by the invariant "No fabrication".

## 6. Time Model
- **Decision**: All timestamps are stored and processed in absolute UTC. Frames/observations will explicitly carry both video offset (`source_pts_ms`) and absolute `source_timestamp_utc`.
- **Reason**: Dealing with multiple cameras inherently means dealing with clock drift and varying timezones. A rigid adherence to UTC and exact PTS (Presentation Time Stamp) offsets ensures accurate multi-camera temporal cross-referencing.

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .base import Base

def utc_now():
    return datetime.now(timezone.utc)

class Gateway(Base):
    __tablename__ = 'gateway'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ONLINE")

class Camera(Base):
    __tablename__ = 'camera'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, default="file")
    location: Mapped[str] = mapped_column(String, nullable=True)
    gateway_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('gateway.id'), nullable=True)
    stream_url: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="OFFLINE")
    clock_offset_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class CameraZone(Base):
    __tablename__ = 'camera_zone'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Storing normalized coordinates as JSON
    polygon: Mapped[dict] = mapped_column(JSONB, nullable=False)

class VideoFile(Base):
    __tablename__ = 'video_file'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'))
    capture_start_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[str] = mapped_column(String, nullable=False) # user_supplied | unanchored etc.
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    codec: Mapped[str] = mapped_column(String, nullable=True)
    fps: Mapped[float] = mapped_column(Float, nullable=True)
    duration_s: Mapped[float] = mapped_column(Float, nullable=True)
    checksum: Mapped[str] = mapped_column(String, nullable=True)

class Job(Base):
    __tablename__ = 'job'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="QUEUED") # QUEUED|RUNNING|COMPLETED|FAILED|CANCELLED
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[dict] = mapped_column(JSONB, nullable=True)

class Frame(Base):
    __tablename__ = 'frame'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('video_file.id'))
    timestamp_s: Mapped[float] = mapped_column(Float, nullable=False)
    frame_path: Mapped[str] = mapped_column(String, nullable=False)

class Detection(Base):
    __tablename__ = 'detection'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('frame.id'))
    label: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox: Mapped[dict] = mapped_column(JSONB, nullable=True)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Evidence(Base):
    __tablename__ = 'evidence'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('video_file.id'))
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'))
    timestamp_s: Mapped[float] = mapped_column(Float, nullable=False)
    frame_path: Mapped[str] = mapped_column(String, nullable=False)
    clip_path: Mapped[str] = mapped_column(String, nullable=True)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('event.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class QueryHistory(Base):
    __tablename__ = 'query_history'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query: Mapped[str] = mapped_column(String, nullable=False)
    parsed_query: Mapped[dict] = mapped_column(JSONB, nullable=True)
    response: Mapped[str] = mapped_column(Text, nullable=True)
    result_ids: Mapped[dict] = mapped_column(JSONB, nullable=True)
    latency_s: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

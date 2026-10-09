import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Index, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .base import Base

class Track(Base):
    __tablename__ = 'track'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'))
    status: Mapped[str] = mapped_column(String, default="CREATED") # CREATED, ACTIVE, LOST, ENDED
    trajectory: Mapped[dict] = mapped_column(JSONB, nullable=True)

class Event(Base):
    __tablename__ = 'event'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'), nullable=False)
    timestamp_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timestamp_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    track_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('track.id'), nullable=True)
    global_identity_id: Mapped[str] = mapped_column(String, nullable=True)
    object_type: Mapped[str] = mapped_column(String, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True)
    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera_zone.id'), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    frame_ref: Mapped[str] = mapped_column(String, nullable=True)
    clip_ref: Mapped[str] = mapped_column(String, nullable=True)
    pipeline_version: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        Index('ix_event_camera_time', 'camera_id', 'timestamp_start'),
        Index('ix_event_type', 'event_type'),
        Index('ix_event_identity', 'global_identity_id'),
        Index('ix_event_track', 'track_id'),
        Index('ix_event_attrs', 'attributes', postgresql_using='gin'),
    )

class SceneMemory(Base):
    __tablename__ = 'scene_memory'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'), nullable=False)
    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera_zone.id'), nullable=True)
    aliases: Mapped[dict] = mapped_column(JSONB, default=list) # List of alternative names
    version: Mapped[int] = mapped_column(Integer, default=1)

class Alert(Base):
    __tablename__ = 'alert'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standing_query_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('standing_query.id'), nullable=False)
    camera_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('camera.id'), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    frame_path: Mapped[str] = mapped_column(String, nullable=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

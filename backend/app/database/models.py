from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .connection import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float, nullable=True)
    fps = Column(Float, nullable=True)
    resolution = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")

    vehicle_events = relationship(
        "VehicleEvent",
        back_populates="video",
        cascade="all, delete-orphan"
    )

    vehicle_counts = relationship(
        "VehicleCount",
        back_populates="video",
        cascade="all, delete-orphan"
    )

    processing_jobs = relationship(
        "ProcessingJob",
        back_populates="video",
        cascade="all, delete-orphan"
    )


class VehicleEvent(Base):
    __tablename__ = "vehicle_events"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)

    track_id = Column(Integer, nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    direction = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=True)

    crossed_at = Column(DateTime(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="vehicle_events")


class VehicleCount(Base):
    __tablename__ = "vehicle_counts"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)

    vehicle_type = Column(String(50), nullable=False)
    direction = Column(String(20), nullable=False)
    count = Column(Integer, default=0)

    video = relationship("Video", back_populates="vehicle_counts")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)

    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    video = relationship("Video", back_populates="processing_jobs")
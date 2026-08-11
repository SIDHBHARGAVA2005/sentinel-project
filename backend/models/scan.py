"""Scan model — represents a full attack surface scan job."""
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from db.database import Base


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    target = Column(String, nullable=False, index=True)
    status = Column(SAEnum(ScanStatus), default=ScanStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_assets = Column(Integer, default=0)
    total_vulns = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    assets = relationship("Asset", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")

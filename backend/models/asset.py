"""Asset model — discovered external asset (subdomain, IP, port, service)."""
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    asset_type = Column(String, nullable=False)  # subdomain, ip, port, service
    value = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    protocol = Column(String, nullable=True)
    service = Column(String, nullable=True)
    banner = Column(Text, nullable=True)
    country = Column(String, nullable=True)
    org = Column(String, nullable=True)
    risk_level = Column(String, default="low")  # low, medium, high, critical
    risk_score = Column(Float, default=0.0)
    tags = Column(JSON, default=list)
    raw_data = Column(JSON, default=dict)
    discovered_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="assets")
    vulnerabilities = relationship("Vulnerability", back_populates="asset", cascade="all, delete-orphan")

"""Report model — AI-generated risk assessment reports."""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    executive_summary = Column(Text, nullable=True)
    technical_details = Column(Text, nullable=True)
    risk_score = Column(Integer, default=0)
    recommendations = Column(JSON, default=list)
    threat_actors = Column(JSON, default=list)
    attack_vectors = Column(JSON, default=list)
    remediation_plan = Column(JSON, default=list)
    generated_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="reports")

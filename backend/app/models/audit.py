import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Audit(Base):
    __tablename__ = "audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String(36), ForeignKey("websites.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    health_score = Column(Float, default=100.0)
    pages_crawled = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    website = relationship("Website", back_populates="audits")
    issues = relationship("SEOIssue", back_populates="audit", cascade="all, delete-orphan", lazy="selectin")
    change_plans = relationship("ChangePlan", back_populates="audit")

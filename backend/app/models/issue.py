import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class SEOIssue(Base):
    __tablename__ = "seo_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String(36), ForeignKey("websites.id"), nullable=False)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False)
    
    category = Column(String(50), nullable=False)  # technical, meta, content, links, performance, indexing
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    title = Column(String(255), nullable=False)
    url_or_file = Column(String(500), nullable=False)
    evidence = Column(Text, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=True)
    recommended_fix = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    status = Column(String(50), default="open")  # open, in_plan, resolved, ignored
    created_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="issues")
    audit = relationship("Audit", back_populates="issues")

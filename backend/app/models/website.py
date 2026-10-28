import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    canonical_url = Column(String(255), nullable=False, unique=True)
    local_repo_path = Column(String(500), nullable=True)
    git_remote_url = Column(String(500), nullable=True)
    gsc_site_url = Column(String(255), nullable=True)
    ga4_property_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audits = relationship("Audit", back_populates="website", cascade="all, delete-orphan")
    issues = relationship("SEOIssue", back_populates="website", cascade="all, delete-orphan")
    change_plans = relationship("ChangePlan", back_populates="website", cascade="all, delete-orphan")

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ChangePlan(Base):
    __tablename__ = "change_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    website_id = Column(String(36), ForeignKey("websites.id"), nullable=False)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending_approval")  # pending_approval, approved, applied, rejected, failed, rolled_back
    
    # JSON strings storing detailed structured data
    changes_json = Column(Text, nullable=False)  # List of {file_path, original_snippet, new_snippet, diff, action}
    risk_assessment = Column(Text, nullable=True)
    tests_to_run = Column(Text, nullable=True)  # List of shell commands e.g. ["npm run build", "pytest"]
    rollback_snapshot = Column(Text, nullable=True)  # Backup copies before modifications
    
    execution_log = Column(Text, nullable=True)
    git_commit_hash = Column(String(100), nullable=True)
    git_commit_message = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, nullable=True)

    website = relationship("Website", back_populates="change_plans")
    audit = relationship("Audit", back_populates="change_plans")

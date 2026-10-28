import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float
from backend.app.database import Base

class AIProviderConfig(Base):
    __tablename__ = "ai_providers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_name = Column(String(50), nullable=False, unique=True)  # gemini, claude, openai, meta
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1 is highest priority
    model_name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=True)
    health_status = Column(String(50), default="unknown")  # healthy, degraded, quota_exceeded, error, unknown
    last_latency_ms = Column(Float, nullable=True)
    last_tested_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


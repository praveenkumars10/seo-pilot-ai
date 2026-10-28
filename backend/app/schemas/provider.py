from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AIProviderUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None
    model_name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None

class AIProviderResponse(BaseModel):
    id: str
    provider_name: str
    is_enabled: bool
    priority: int
    model_name: str
    base_url: Optional[str] = None
    health_status: str
    last_latency_ms: Optional[float] = None
    last_tested_at: Optional[datetime] = None
    last_error: Optional[str] = None
    has_api_key: bool = False

    model_config = ConfigDict(from_attributes=True)

class ProviderTestResponse(BaseModel):
    provider_name: str
    status: str
    latency_ms: float
    message: str

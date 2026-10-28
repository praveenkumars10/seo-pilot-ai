from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class WebsiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    canonical_url: str = Field(..., max_length=255)
    local_repo_path: Optional[str] = None
    git_remote_url: Optional[str] = None
    gsc_site_url: Optional[str] = None
    ga4_property_id: Optional[str] = None
    description: Optional[str] = None

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    canonical_url: Optional[str] = None
    local_repo_path: Optional[str] = None
    git_remote_url: Optional[str] = None
    gsc_site_url: Optional[str] = None
    ga4_property_id: Optional[str] = None
    description: Optional[str] = None

class WebsiteResponse(WebsiteBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

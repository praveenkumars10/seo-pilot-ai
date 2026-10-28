from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class SEOIssueResponse(BaseModel):
    id: str
    website_id: str
    audit_id: str
    category: str
    severity: str
    title: str
    url_or_file: str
    evidence: Optional[str] = None
    root_cause_hypothesis: Optional[str] = None
    recommended_fix: Optional[str] = None
    confidence: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditResponse(BaseModel):
    id: str
    website_id: str
    status: str
    health_score: float
    pages_crawled: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    summary: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    issues: Optional[List[SEOIssueResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class AuditTriggerRequest(BaseModel):
    website_id: str
    max_pages: Optional[int] = 20
    include_code_analysis: bool = True

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileModification(BaseModel):
    file_path: str
    action: str  # modify, create, delete
    original_snippet: Optional[str] = None
    new_snippet: Optional[str] = None
    diff: str
    reason: str
    target_issues: List[str]

class ChangePlanResponse(BaseModel):
    id: str
    website_id: str
    audit_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    changes: List[FileModification] = []
    risk_assessment: Optional[str] = None
    tests_to_run: List[str] = []
    execution_log: Optional[str] = None
    git_commit_hash: Optional[str] = None
    git_commit_message: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(approve|reject)$")
    custom_commit_message: Optional[str] = None
    auto_git_push: bool = False
    run_tests: bool = True

class PlanGenerationRequest(BaseModel):
    website_id: str
    audit_id: Optional[str] = None
    issue_ids: Optional[List[str]] = None
    provider_name: Optional[str] = None

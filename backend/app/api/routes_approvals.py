import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.database import get_db
from backend.app.models.website import Website
from backend.app.models.audit import Audit
from backend.app.models.issue import SEOIssue
from backend.app.models.change_plan import ChangePlan
from backend.app.schemas.approval import (
    PlanGenerationRequest,
    ChangePlanResponse,
    ApprovalDecisionRequest,
    FileModification
)
from backend.app.services.ai.orchestrator import ai_orchestrator
from backend.app.services.code_modifier import CodeModifierService
from backend.app.services.git_service import GitService

router = APIRouter(prefix="/approvals", tags=["Consolidated Approvals"])
logger = logging.getLogger(__name__)

def _format_plan_response(plan: ChangePlan) -> ChangePlanResponse:
    try:
        raw_changes = json.loads(plan.changes_json) if plan.changes_json else []
    except Exception:
        raw_changes = []

    try:
        raw_tests = json.loads(plan.tests_to_run) if plan.tests_to_run else []
    except Exception:
        raw_tests = []

    modifications = [
        FileModification(
            file_path=item.get("file_path", ""),
            action=item.get("action", "modify"),
            original_snippet=item.get("original_snippet"),
            new_snippet=item.get("new_snippet"),
            diff=item.get("diff", ""),
            reason=item.get("reason", ""),
            target_issues=item.get("target_issues", [])
        )
        for item in raw_changes
    ]

    return ChangePlanResponse(
        id=plan.id,
        website_id=plan.website_id,
        audit_id=plan.audit_id,
        title=plan.title,
        description=plan.description,
        status=plan.status,
        changes=modifications,
        risk_assessment=plan.risk_assessment,
        tests_to_run=raw_tests,
        execution_log=plan.execution_log,
        git_commit_hash=plan.git_commit_hash,
        git_commit_message=plan.git_commit_message,
        created_at=plan.created_at,
        approved_at=plan.approved_at,
        applied_at=plan.applied_at
    )

@router.post("/generate", response_model=ChangePlanResponse)
async def generate_change_plan(
    payload: PlanGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes a consolidated ChangePlan for open SEO issues.
    Does NOT touch files until the user explicitly approves this plan.
    """
    web_res = await db.execute(select(Website).where(Website.id == payload.website_id))
    website = web_res.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    if not website.local_repo_path:
        raise HTTPException(
            status_code=400,
            detail="Local repository path is not configured for this website. Cannot prepare code changes."
        )

    # Gather issues
    if payload.issue_ids:
        iss_res = await db.execute(
            select(SEOIssue)
            .where(SEOIssue.id.in_(payload.issue_ids))
            .where(SEOIssue.website_id == website.id)
        )
        issues = iss_res.scalars().all()
    else:
        # Default: get top open critical/high issues from latest audit
        iss_res = await db.execute(
            select(SEOIssue)
            .where(SEOIssue.website_id == website.id)
            .where(SEOIssue.status == "open")
            .limit(15)
        )
        issues = iss_res.scalars().all()

    if not issues:
        raise HTTPException(status_code=400, detail="No open SEO issues found to prepare a plan for.")

    issue_dicts = [
        {
            "id": i.id,
            "title": i.title,
            "category": i.category,
            "severity": i.severity,
            "url_or_file": i.url_or_file,
            "evidence": i.evidence,
            "root_cause_hypothesis": i.root_cause_hypothesis,
            "recommended_fix": i.recommended_fix
        }
        for i in issues
    ]

    project_context = {
        "name": website.name,
        "canonical_url": website.canonical_url,
        "local_repo_path": website.local_repo_path,
        "framework": "React / HTML"
    }

    # Generate fixes via AI Orchestrator
    plan_data = await ai_orchestrator.generate_change_plan(
        issues=issue_dicts,
        project_context=project_context,
        preferred_provider=payload.provider_name
    )

    fixes = plan_data.get("fixes", [])
    if not fixes:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate safe code diffs for the selected issues."
        )

    # Create ChangePlan record
    new_plan = ChangePlan(
        website_id=website.id,
        audit_id=payload.audit_id,
        title=f"SEO Optimization Batch: {len(fixes)} fix(es) prepared ({plan_data.get('provider_used')})",
        description=f"Automated resolution plan for {len(issues)} detected SEO issues.",
        status="pending_approval",
        changes_json=json.dumps(fixes),
        risk_assessment=plan_data.get("risk_assessment", "low"),
        tests_to_run=json.dumps(plan_data.get("tests_to_run", ["npm test"]))
    )
    db.add(new_plan)

    # Mark issues as in_plan
    for i in issues:
        i.status = "in_plan"

    await db.commit()
    await db.refresh(new_plan)

    return _format_plan_response(new_plan)

@router.get("/pending", response_model=List[ChangePlanResponse])
async def list_pending_approvals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChangePlan)
        .where(ChangePlan.status == "pending_approval")
        .order_by(ChangePlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [_format_plan_response(p) for p in plans]

@router.get("/{plan_id}", response_model=ChangePlanResponse)
async def get_plan_details(plan_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChangePlan).where(ChangePlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Change plan not found.")
    return _format_plan_response(plan)

@router.post("/{plan_id}/decision", response_model=ChangePlanResponse)
async def submit_approval_decision(
    plan_id: str,
    payload: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Consolidated Approval Gatekeeper.
    Applies the entire batch upon approval, runs tests, creates Git commit, and optionally pushes.
    """
    result = await db.execute(select(ChangePlan).where(ChangePlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Change plan not found.")

    if plan.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Plan cannot be modified. Current status is '{plan.status}'."
        )

    web_res = await db.execute(select(Website).where(Website.id == plan.website_id))
    website = web_res.scalar_one_or_none()

    if payload.decision == "reject":
        plan.status = "rejected"
        plan.execution_log = "Plan rejected by user during consolidated review."
        await db.commit()
        await db.refresh(plan)
        return _format_plan_response(plan)

    # Approved: Execute batch
    plan.status = "approved"
    plan.approved_at = datetime.utcnow()
    await db.commit()

    changes = json.loads(plan.changes_json)
    tests = json.loads(plan.tests_to_run) if plan.tests_to_run else []

    modifier = CodeModifierService(repo_path=website.local_repo_path)
    exec_result = modifier.apply_plan(
        changes=changes,
        run_tests=payload.run_tests,
        test_commands=tests
    )

    plan.execution_log = exec_result.get("execution_log", "")

    if not exec_result.get("success"):
        plan.status = "rolled_back" if exec_result.get("rolled_back") else "failed"
        await db.commit()
        await db.refresh(plan)
        return _format_plan_response(plan)

    # Code changes succeeded and tests passed!
    plan.status = "applied"
    plan.applied_at = datetime.utcnow()

    # Step: Git commit
    affected_files = [c.get("file_path") for c in changes if c.get("file_path")]
    commit_msg = payload.custom_commit_message or f"fix(seo): apply approved optimization batch ({len(changes)} files)"

    git_service = GitService(repo_path=website.local_repo_path)
    commit_res = git_service.commit_approved_changes(
        files=affected_files,
        commit_message=commit_msg
    )

    if commit_res.get("success"):
        plan.git_commit_hash = commit_res.get("commit_hash")
        plan.git_commit_message = commit_msg
        plan.execution_log += f"\n[Git] Successfully created commit {commit_res.get('commit_hash')}"

        # Step: Git push if authorized
        if payload.auto_git_push and website.git_remote_url:
            push_res = git_service.push_to_remote()
            if push_res.get("success"):
                plan.execution_log += f"\n[Git] {push_res.get('message')}"
            else:
                plan.execution_log += f"\n[Git Push Warning] {push_res.get('error')}"

    # Mark associated issues as resolved
    iss_res = await db.execute(
        select(SEOIssue)
        .where(SEOIssue.website_id == website.id)
        .where(SEOIssue.status == "in_plan")
    )
    for issue in iss_res.scalars().all():
        issue.status = "resolved"

    await db.commit()
    await db.refresh(plan)

    return _format_plan_response(plan)

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.database import get_db
from backend.app.models.website import Website
from backend.app.models.audit import Audit
from backend.app.services.scheduler import audit_scheduler

router = APIRouter(prefix="/monitoring", tags=["Scheduling & Monitoring"])
logger = logging.getLogger(__name__)

@router.get("/schedules")
def get_all_schedules():
    """Retrieve all automated recurring audit schedules."""
    return audit_scheduler.list_schedules()

@router.post("/schedule")
def configure_schedule(
    website_id: str = Body(..., embed=True),
    interval_hours: int = Body(24, ge=1, le=168, embed=True)
):
    """Set recurring audit interval (hours) for a website."""
    return audit_scheduler.schedule_website(website_id=website_id, interval_hours=interval_hours)

@router.post("/pause")
def pause_schedule(website_id: str = Body(..., embed=True)):
    return audit_scheduler.pause_schedule(website_id=website_id)

@router.post("/resume")
def resume_schedule(website_id: str = Body(..., embed=True)):
    return audit_scheduler.resume_schedule(website_id=website_id)

@router.get("/comparison/{website_id}")
async def get_audit_comparison(website_id: str, db: AsyncSession = Depends(get_db)):
    """
    Compares the most recent audit with the previous audit:
    - Score delta (improvement or regression)
    - Newly introduced issues
    - Resolved issues
    """
    res = await db.execute(
        select(Audit)
        .options(selectinload(Audit.issues))
        .where(Audit.website_id == website_id)
        .where(Audit.status == "completed")
        .order_by(Audit.created_at.desc())
        .limit(2)
    )
    audits = res.scalars().all()

    if not audits:
        return {
            "has_history": False,
            "message": "No completed audits found for this website."
        }

    latest = audits[0]
    previous = audits[1] if len(audits) > 1 else None

    latest_issue_titles = {i.title for i in latest.issues} if latest.issues else set()
    prev_issue_titles = {i.title for i in previous.issues} if previous and previous.issues else set()

    newly_introduced = list(latest_issue_titles - prev_issue_titles)
    resolved_issues = list(prev_issue_titles - latest_issue_titles) if previous else []

    score_delta = round(latest.health_score - previous.health_score, 1) if previous else 0.0

    return {
        "has_history": True,
        "latest_audit_id": latest.id,
        "latest_score": latest.health_score,
        "previous_score": previous.health_score if previous else None,
        "score_delta": score_delta,
        "status_trend": "improved" if score_delta > 0 else "regressed" if score_delta < 0 else "neutral",
        "total_current_issues": latest.total_issues,
        "newly_introduced_issues": newly_introduced,
        "resolved_issues": resolved_issues,
        "latest_date": latest.created_at.isoformat(),
        "previous_date": previous.created_at.isoformat() if previous else None
    }


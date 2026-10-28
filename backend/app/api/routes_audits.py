import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.database import get_db, AsyncSessionLocal
from backend.app.models.website import Website
from backend.app.models.audit import Audit
from backend.app.models.issue import SEOIssue
from backend.app.schemas.audit import AuditResponse, SEOIssueResponse, AuditTriggerRequest
from backend.app.services.crawler import SEOCrawlerService
from backend.app.services.code_analyzer import LocalCodeAnalyzerService

router = APIRouter(prefix="/audits", tags=["Audits & Crawler"])
logger = logging.getLogger(__name__)

async def run_audit_background(audit_id: str, website_id: str, max_pages: int, include_code_analysis: bool):
    """Executes crawler and source code analyzer in background task."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Website).where(Website.id == website_id))
        website = res.scalar_one_or_none()
        if not website:
            return

        audit_res = await db.execute(select(Audit).where(Audit.id == audit_id))
        audit = audit_res.scalar_one_or_none()
        if not audit:
            return

        audit.status = "running"
        await db.commit()

        try:
            # 1. Run live crawler
            crawler = SEOCrawlerService(base_url=website.canonical_url, max_pages=max_pages)
            crawl_summary = await crawler.crawl_site()

            # 2. Run local code analyzer if local path exists
            code_issues = []
            if include_code_analysis and website.local_repo_path:
                analyzer = LocalCodeAnalyzerService(repo_path=website.local_repo_path)
                code_issues = analyzer.analyze_repository()

            # Merge and deduplicate issues
            all_raw_issues = crawl_summary["issues"] + code_issues

            # Save issues into DB
            crit_count = 0
            high_count = 0
            med_count = 0
            low_count = 0

            for raw in all_raw_issues:
                sev = raw.get("severity", "medium")
                if sev == "critical":
                    crit_count += 1
                elif sev == "high":
                    high_count += 1
                elif sev == "medium":
                    med_count += 1
                elif sev == "low":
                    low_count += 1

                issue = SEOIssue(
                    website_id=website.id,
                    audit_id=audit.id,
                    category=raw.get("category", "technical"),
                    severity=sev,
                    title=raw.get("title", "SEO Issue"),
                    url_or_file=raw.get("url_or_file", ""),
                    evidence=raw.get("evidence", ""),
                    root_cause_hypothesis=raw.get("root_cause_hypothesis", ""),
                    recommended_fix=raw.get("recommended_fix", ""),
                    confidence=raw.get("confidence", 0.9),
                    status="open"
                )
                db.add(issue)

            # Re-compute total score based on combined findings
            deduction = (crit_count * 12) + (high_count * 7) + (med_count * 3) + (low_count * 1)
            final_score = max(5.0, round(100.0 - deduction, 1))

            audit.status = "completed"
            audit.health_score = final_score
            audit.pages_crawled = crawl_summary.get("pages_crawled", 1)
            audit.total_issues = len(all_raw_issues)
            audit.critical_issues = crit_count
            audit.high_issues = high_count
            audit.medium_issues = med_count
            audit.low_issues = low_count
            audit.summary = (
                f"Audit successfully identified {len(all_raw_issues)} total issues "
                f"({crit_count} critical, {high_count} high) across {audit.pages_crawled} crawled page(s) "
                f"and local code files."
            )
            audit.completed_at = datetime.utcnow()

            await db.commit()

        except Exception as e:
            logger.error(f"Audit failed for website {website_id}: {e}", exc_info=True)
            audit.status = "failed"
            audit.summary = f"Audit encountered an error: {str(e)}"
            await db.commit()

@router.post("/trigger", response_model=AuditResponse)
async def trigger_audit(
    payload: AuditTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    website_res = await db.execute(select(Website).where(Website.id == payload.website_id))
    website = website_res.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    audit = Audit(
        website_id=website.id,
        status="pending",
        health_score=100.0
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)

    background_tasks.add_task(
        run_audit_background,
        audit.id,
        website.id,
        payload.max_pages or 20,
        payload.include_code_analysis
    )

    return audit

@router.get("/website/{website_id}", response_model=List[AuditResponse])
async def list_audits_for_website(website_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Audit)
        .where(Audit.website_id == website_id)
        .order_by(Audit.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit_details(audit_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Audit)
        .options(selectinload(Audit.issues))
        .where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit

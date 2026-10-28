import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from backend.app.database import AsyncSessionLocal
from backend.app.models.website import Website
from backend.app.models.audit import Audit
from backend.app.api.routes_audits import run_audit_background

logger = logging.getLogger(__name__)

class ScheduledAuditJob:
    def __init__(self, website_id: str, interval_hours: int = 24, is_active: bool = True):
        self.website_id = website_id
        self.interval_hours = interval_hours
        self.is_active = is_active
        self.last_run_at: Optional[datetime] = None
        self.next_run_at: datetime = datetime.utcnow() + timedelta(hours=interval_hours)

class AuditScheduler:
    def __init__(self):
        self.jobs: Dict[str, ScheduledAuditJob] = {}
        self.running: bool = False
        self._task: Optional[asyncio.Task] = None

    def schedule_website(self, website_id: str, interval_hours: int = 24) -> Dict[str, Any]:
        """Configure or update recurring audit schedule for a website."""
        job = ScheduledAuditJob(website_id=website_id, interval_hours=interval_hours, is_active=True)
        self.jobs[website_id] = job
        return {
            "website_id": website_id,
            "interval_hours": interval_hours,
            "is_active": True,
            "next_run_at": job.next_run_at.isoformat()
        }

    def pause_schedule(self, website_id: str) -> Dict[str, Any]:
        if website_id in self.jobs:
            self.jobs[website_id].is_active = False
            return {"website_id": website_id, "is_active": False}
        return {"error": "Website not scheduled"}

    def resume_schedule(self, website_id: str) -> Dict[str, Any]:
        if website_id in self.jobs:
            self.jobs[website_id].is_active = True
            self.jobs[website_id].next_run_at = datetime.utcnow() + timedelta(hours=self.jobs[website_id].interval_hours)
            return {"website_id": website_id, "is_active": True, "next_run_at": self.jobs[website_id].next_run_at.isoformat()}
        return {"error": "Website not scheduled"}

    def list_schedules(self) -> List[Dict[str, Any]]:
        return [
            {
                "website_id": j.website_id,
                "interval_hours": j.interval_hours,
                "is_active": j.is_active,
                "last_run_at": j.last_run_at.isoformat() if j.last_run_at else None,
                "next_run_at": j.next_run_at.isoformat() if j.next_run_at else None
            }
            for j in self.jobs.values()
        ]

    async def start(self):
        """Starts background monitoring loop."""
        self.running = True
        logger.info("Audit Scheduler daemon started.")
        while self.running:
            try:
                now = datetime.utcnow()
                for site_id, job in list(self.jobs.items()):
                    if job.is_active and now >= job.next_run_at:
                        logger.info(f"Triggering scheduled recurring audit for website: {site_id}")
                        job.last_run_at = now
                        job.next_run_at = now + timedelta(hours=job.interval_hours)
                        asyncio.create_task(self._execute_scheduled_audit(site_id))
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}")

            await asyncio.sleep(60)  # Check every minute

    async def _execute_scheduled_audit(self, website_id: str):
        async with AsyncSessionLocal() as db:
            audit = Audit(website_id=website_id, status="pending", health_score=100.0)
            db.add(audit)
            await db.commit()
            await db.refresh(audit)
            await run_audit_background(
                audit_id=audit.id,
                website_id=website_id,
                max_pages=20,
                include_code_analysis=True
            )

    def stop(self):
        self.running = False

audit_scheduler = AuditScheduler()


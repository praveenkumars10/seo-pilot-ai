import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import select
from backend.app.database import init_db, AsyncSessionLocal
from backend.app.models.website import Website
from backend.app.models.audit import Audit
from backend.app.models.issue import SEOIssue
from backend.app.models.change_plan import ChangePlan
from backend.app.services.ai.orchestrator import ai_orchestrator
from backend.app.services.code_analyzer import LocalCodeAnalyzerService
import json

async def seed_showcase_data():
    await init_db()
    root_dir = Path(__file__).resolve().parent.parent.parent
    showcase_path = str(root_dir / "showcase_website").replace("\\", "/")

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        existing = await db.execute(select(Website).where(Website.canonical_url == "https://showcase.enterprisecorp.io"))
        if existing.scalar_one_or_none():
            print("Showcase site already registered.")
            return

        # 1. Create Website
        site = Website(
            name="Showcase Enterprise Portal",
            canonical_url="https://showcase.enterprisecorp.io",
            local_repo_path=showcase_path,
            description="Demonstration web application showcasing autonomous SEO code modifications and approval gates."
        )
        db.add(site)
        await db.commit()
        await db.refresh(site)

        # 2. Run local code analyzer
        analyzer = LocalCodeAnalyzerService(repo_path=showcase_path)
        issues_raw = analyzer.analyze_repository()

        audit = Audit(
            website_id=site.id,
            status="completed",
            health_score=78.5,
            pages_crawled=1,
            total_issues=len(issues_raw),
            critical_issues=sum(1 for i in issues_raw if i.get("severity") == "critical"),
            high_issues=sum(1 for i in issues_raw if i.get("severity") == "high"),
            medium_issues=sum(1 for i in issues_raw if i.get("severity") == "medium"),
            low_issues=sum(1 for i in issues_raw if i.get("severity") == "low"),
            summary=f"Audit completed: {len(issues_raw)} technical SEO issues detected in codebase."
        )
        db.add(audit)
        await db.commit()
        await db.refresh(audit)

        db_issues = []
        for raw in issues_raw:
            iss = SEOIssue(
                website_id=site.id,
                audit_id=audit.id,
                category=raw.get("category", "technical"),
                severity=raw.get("severity", "medium"),
                title=raw.get("title", ""),
                url_or_file=raw.get("url_or_file", ""),
                evidence=raw.get("evidence", ""),
                root_cause_hypothesis=raw.get("root_cause_hypothesis", ""),
                recommended_fix=raw.get("recommended_fix", ""),
                status="in_plan"
            )
            db.add(iss)
            db_issues.append({
                "title": raw.get("title", ""),
                "url_or_file": raw.get("url_or_file", ""),
                "original_snippet": raw.get("original_snippet", ""),
                "evidence": raw.get("evidence", "")
            })

        await db.commit()

        # 3. Generate Consolidated ChangePlan
        plan_data = await ai_orchestrator.generate_change_plan(
            issues=db_issues,
            project_context={
                "name": site.name,
                "canonical_url": site.canonical_url,
                "local_repo_path": showcase_path,
                "framework": "HTML"
            }
        )

        fixes = plan_data.get("fixes", [])
        if fixes:
            plan = ChangePlan(
                website_id=site.id,
                audit_id=audit.id,
                title=f"Showcase SEO Optimization Batch: {len(fixes)} fix(es) prepared",
                description="Consolidated resolution batch for title optimization, missing alt attributes, robots.txt, and sitemap.xml.",
                status="pending_approval",
                changes_json=json.dumps(fixes),
                risk_assessment="low",
                tests_to_run=json.dumps([])
            )
            db.add(plan)
            await db.commit()

        print("Successfully seeded showcase website, audit, and pending approval plan!")

if __name__ == "__main__":
    asyncio.run(seed_showcase_data())

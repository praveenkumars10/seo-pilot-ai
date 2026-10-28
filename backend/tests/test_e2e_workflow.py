import pytest
import uuid
import git
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db
from backend.app.api.routes_audits import run_audit_background

@pytest.mark.asyncio
async def test_full_autonomous_seo_loop(tmp_path):
    await init_db()

    # 1. Prepare sample website project folder
    test_repo = tmp_path / "sample_website"
    test_repo.mkdir()
    index_file = test_repo / "index.html"
    index_file.write_text("""<!DOCTYPE html>
<html>
  <head>
    <title>Vite + React + TS</title>
  </head>
  <body>
    <img src="/hero.png" />
    <div id="root"></div>
  </body>
</html>
""", encoding="utf-8")

    # Initialize git repo in sample project
    repo = git.Repo.init(test_repo)
    with repo.config_writer() as config:
        config.set_value("user", "name", "SEO Test Runner")
        config.set_value("user", "email", "runner@test.local")
    repo.index.add(["index.html"])
    repo.index.commit("initial commit")

    unique_url = f"https://e2e-{uuid.uuid4().hex[:8]}.local"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 2. Register Website
        reg_res = await ac.post("/api/websites", json={
            "name": "E2E Sample Site",
            "canonical_url": unique_url,
            "local_repo_path": str(test_repo)
        })
        assert reg_res.status_code == 201
        site_id = reg_res.json()["id"]

        # 3. Trigger Audit
        audit_trigger = await ac.post("/api/audits/trigger", json={
            "website_id": site_id,
            "max_pages": 5,
            "include_code_analysis": True
        })
        assert audit_trigger.status_code == 200
        audit_id = audit_trigger.json()["id"]

        # Execute the background audit function directly to await completion
        await run_audit_background(
            audit_id=audit_id,
            website_id=site_id,
            max_pages=5,
            include_code_analysis=True
        )

        # 4. Check audit results and issues
        audit_res = await ac.get(f"/api/audits/{audit_id}")
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert audit_data["status"] == "completed"
        assert audit_data["total_issues"] > 0

        # 5. Generate Consolidated ChangePlan
        plan_gen_res = await ac.post("/api/approvals/generate", json={
            "website_id": site_id,
            "audit_id": audit_id
        })
        assert plan_gen_res.status_code == 200
        plan = plan_gen_res.json()
        assert plan["status"] == "pending_approval"
        assert len(plan["changes"]) > 0

        # Assert no file was changed BEFORE approval
        assert not (test_repo / "public" / "robots.txt").exists()

        # 6. User submits Consolidated Approval
        approval_res = await ac.post(f"/api/approvals/{plan['id']}/decision", json={
            "decision": "approve",
            "auto_git_push": False,
            "custom_commit_message": "fix(seo): apply autonomous e2e optimization batch"
        })
        assert approval_res.status_code == 200
        approved_plan = approval_res.json()
        assert approved_plan["status"] == "applied", f"Execution failed:\n{approved_plan.get('execution_log')}"
        assert approved_plan["git_commit_hash"] is not None

        # 7. Verify disk changes AFTER approval
        updated_index = index_file.read_text(encoding="utf-8")
        assert "E2E Sample Site" in updated_index  # Title optimized!
        assert (test_repo / "public" / "robots.txt").exists()  # robots.txt generated!

        # Verify git commit in the target repository
        assert repo.head.commit.hexsha == approved_plan["git_commit_hash"]
        assert "autonomous e2e optimization" in repo.head.commit.message

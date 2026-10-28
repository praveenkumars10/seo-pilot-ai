import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db

@pytest.mark.asyncio
async def test_scheduler_and_monitoring_endpoints():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Schedule an audit
        sched_res = await ac.post("/api/monitoring/schedule", json={
            "website_id": "test-site-sched-1",
            "interval_hours": 12
        })
        assert sched_res.status_code == 200
        sched_data = sched_res.json()
        assert sched_data["interval_hours"] == 12
        assert sched_data["is_active"] is True

        # List schedules
        list_res = await ac.get("/api/monitoring/schedules")
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # Pause
        pause_res = await ac.post("/api/monitoring/pause", json={"website_id": "test-site-sched-1"})
        assert pause_res.status_code == 200
        assert pause_res.json()["is_active"] is False

        # Resume
        resume_res = await ac.post("/api/monitoring/resume", json={"website_id": "test-site-sched-1"})
        assert resume_res.status_code == 200
        assert resume_res.json()["is_active"] is True

        # Comparison (no history yet)
        comp_res = await ac.get("/api/monitoring/comparison/non-existent-site")
        assert comp_res.status_code == 200
        assert comp_res.json()["has_history"] is False


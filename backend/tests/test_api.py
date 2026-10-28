import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import init_db

@pytest.mark.asyncio
async def test_health_check_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["approval_gatekeeper"] == "active"

@pytest.mark.asyncio
async def test_websites_crud_and_ai_status():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Check AI status
        ai_resp = await ac.get("/api/ai/status")
        assert ai_resp.status_code == 200
        providers = ai_resp.json()
        assert len(providers) >= 4  # gemini, claude, openai, meta

        # Create website
        new_site = {
            "name": "Test Agency Portal",
            "canonical_url": "https://test-agency-portal.com",
            "description": "Production website test"
        }
        create_resp = await ac.post("/api/websites", json=new_site)
        assert create_resp.status_code in [201, 400]
        if create_resp.status_code == 201:
            site_data = create_resp.json()
            assert site_data["id"] is not None
            assert site_data["canonical_url"] == "https://test-agency-portal.com"

        # List websites
        list_resp = await ac.get("/api/websites")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # Check pending approvals endpoint
        pending_resp = await ac.get("/api/approvals/pending")
        assert pending_resp.status_code == 200
        assert isinstance(pending_resp.json(), list)

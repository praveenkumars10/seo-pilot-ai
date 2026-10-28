import pytest
from backend.app.services.ai.orchestrator import AIOrchestrator

@pytest.mark.asyncio
async def test_deterministic_fallback_when_no_api_keys():
    orchestrator = AIOrchestrator()
    # Mock empty API keys
    for prov in orchestrator.providers.values():
        prov.api_key = None

    issues = [
        {
            "title": "Missing robots.txt in Project Webroot",
            "url_or_file": "public/robots.txt",
            "original_snippet": ""
        },
        {
            "title": "Default or Placeholder Page Title in Code",
            "url_or_file": "index.html:5",
            "original_snippet": "<title>Vite + React + TS</title>"
        }
    ]

    project_context = {
        "name": "Acme SaaS",
        "canonical_url": "https://acme.com",
        "framework": "React"
    }

    result = await orchestrator.generate_change_plan(issues, project_context)
    fixes = result["fixes"]

    assert len(fixes) == 2
    assert result["provider_used"] == "deterministic-seo-engine"

    target_files = [f["file_path"] for f in fixes]
    assert "public/robots.txt" in target_files
    assert "index.html" in target_files
    assert "diff" in fixes[0]


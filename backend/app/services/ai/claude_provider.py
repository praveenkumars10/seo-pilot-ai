import json
import time
import httpx
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProviderBase

class ClaudeProvider(AIProviderBase):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-5-sonnet-20241022"):
        super().__init__(
            provider_name="claude",
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.anthropic.com/v1"
        )

    async def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "error",
                "message": "Anthropic API key is not configured.",
                "latency_ms": 0.0
            }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Respond 'OK'"}]
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": f"Successfully connected to Claude ({self.model_name})",
                        "latency_ms": latency
                    }
                elif res.status_code == 429:
                    return {
                        "status": "quota_exceeded",
                        "message": "Anthropic Claude rate limit / balance exhausted.",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Claude API error HTTP {res.status_code}: {res.text[:150]}",
                        "latency_ms": latency
                    }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Network error contacting Claude API: {str(exc)}",
                "latency_ms": 0.0
            }

    async def analyze_and_propose_fixes(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        prompt = f"""
Analyze the following technical SEO issues for {project_context.get('canonical_url', '')} and generate a JSON array of fixes.
Issues:
{json.dumps(issues, indent=2)}

Format requirement: STRICT JSON array of objects with keys: file_path, action, original_snippet, new_snippet, diff, reason, target_issues.
Do not include any text before or after the JSON.
"""
        payload = {
            "model": self.model_name,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["content"][0]["text"].strip()
                    if text.startswith("```json"):
                        text = text[7:-3].strip()
                    elif text.startswith("```"):
                        text = text[3:-3].strip()
                    return json.loads(text)
        except Exception:
            pass

        return []

    async def review_plan_for_regressions(
        self,
        plan_changes: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "skipped", "risk_level": "low", "notes": "No Claude API key"}

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        prompt = f"""
Review these planned code changes for potential syntax or runtime regressions:
{json.dumps(plan_changes, indent=2)}

Return JSON: {{"safe_to_apply": bool, "risk_level": "low"|"medium"|"high", "warnings": list, "recommended_tests": list}}
"""
        payload = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["content"][0]["text"].strip()
                    if text.startswith("```json"):
                        text = text[7:-3].strip()
                    elif text.startswith("```"):
                        text = text[3:-3].strip()
                    return json.loads(text)
        except Exception:
            pass

        return {"safe_to_apply": True, "risk_level": "low", "warnings": []}


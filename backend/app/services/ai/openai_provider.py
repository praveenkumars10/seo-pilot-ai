import json
import time
import httpx
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProviderBase

class OpenAIProvider(AIProviderBase):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        super().__init__(
            provider_name="openai",
            model_name=model_name,
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )

    async def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "error",
                "message": "OpenAI API key is not configured.",
                "latency_ms": 0.0
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 5,
            "messages": [{"role": "user", "content": "Respond OK"}]
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": f"Successfully connected to OpenAI ({self.model_name})",
                        "latency_ms": latency
                    }
                elif res.status_code == 429:
                    return {
                        "status": "quota_exceeded",
                        "message": "OpenAI quota exceeded or rate limited.",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"OpenAI error HTTP {res.status_code}: {res.text[:150]}",
                        "latency_ms": latency
                    }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Network error contacting OpenAI API: {str(exc)}",
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"""
You are an autonomous SEO engineer. Propose unified code diffs to resolve these SEO issues for {project_context.get('canonical_url', '')}:
{json.dumps(issues, indent=2)}

Output JSON array of objects with keys: file_path, action, original_snippet, new_snippet, diff, reason, target_issues.
"""
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You return valid JSON with key 'fixes' containing the list of file modifications."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    return parsed.get("fixes", parsed if isinstance(parsed, list) else [])
        except Exception:
            pass

        return []

    async def review_plan_for_regressions(
        self,
        plan_changes: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"safe_to_apply": True, "risk_level": "low", "warnings": []}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"Analyze these code changes for syntax errors or risks:\n{json.dumps(plan_changes, indent=2)}"
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return JSON with keys safe_to_apply (bool), risk_level ('low'/'medium'/'high'), warnings (list of strings)."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return json.loads(data["choices"][0]["message"]["content"])
        except Exception:
            pass

        return {"safe_to_apply": True, "risk_level": "low", "warnings": []}

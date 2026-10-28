import json
import time
import httpx
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProviderBase

class GeminiProvider(AIProviderBase):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        super().__init__(
            provider_name="gemini",
            model_name=model_name,
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta"
        )

    async def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "error",
                "message": "Gemini API key is not configured.",
                "latency_ms": 0.0
            }

        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Respond with 'OK' if you can read this."}]}]
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": f"Successfully connected to Gemini ({self.model_name})",
                        "latency_ms": latency
                    }
                elif res.status_code == 429:
                    return {
                        "status": "quota_exceeded",
                        "message": "Gemini free rate limit or quota exceeded.",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Gemini API returned HTTP {res.status_code}: {res.text[:150]}",
                        "latency_ms": latency
                    }
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Network error contacting Gemini API: {str(exc)}",
                "latency_ms": 0.0
            }

    async def analyze_and_propose_fixes(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Call Gemini to generate precise code fixes and diffs."""
        if not self.api_key:
            return []

        prompt = f"""
You are an expert Autonomous SEO Engineer.
Analyze the following technical SEO issues for website: {project_context.get('canonical_url', 'N/A')}
Project Framework/Structure: {project_context.get('framework', 'HTML/React')}

Issues to address:
{json.dumps(issues, indent=2)}

Return a strict JSON list of file modifications to solve these issues.
Each item must have:
- file_path: relative path to the file to modify
- action: "modify" or "create"
- original_snippet: exact code snippet before modification
- new_snippet: proposed replacement code snippet
- diff: unified diff string showing changes
- reason: concise explanation of why this change improves SEO
- target_issues: array of issue titles addressed

Do not output any markdown formatting, backticks, or explanation outside of the valid JSON array.
"""
        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:-3].strip()
                    elif cleaned.startswith("```"):
                        cleaned = cleaned[3:-3].strip()
                    return json.loads(cleaned)
        except Exception:
            pass

        return []

    async def review_plan_for_regressions(
        self,
        plan_changes: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform regression safety check with Gemini."""
        if not self.api_key:
            return {"status": "skipped", "risk_level": "low", "notes": "No Gemini API key"}

        prompt = f"""
Review the following proposed SEO code changes for potential syntax regressions, broken imports, or destructive actions:
{json.dumps(plan_changes, indent=2)}

Respond with a JSON object:
{{
  "safe_to_apply": true/false,
  "risk_level": "low" | "medium" | "high",
  "warnings": ["list of potential hazards if any"],
  "recommended_tests": ["shell commands to test, e.g. npm test"]
}}
"""
        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:-3].strip()
                    elif cleaned.startswith("```"):
                        cleaned = cleaned[3:-3].strip()
                    return json.loads(cleaned)
        except Exception:
            pass

        return {"safe_to_apply": True, "risk_level": "low", "warnings": [], "recommended_tests": ["npm test"]}

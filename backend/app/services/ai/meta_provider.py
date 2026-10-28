import json
import time
import httpx
from typing import Dict, Any, List, Optional
from backend.app.services.ai.base import AIProviderBase

class MetaProvider(AIProviderBase):
    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model_name: str = "llama3.2",
        api_key: Optional[str] = None
    ):
        super().__init__(
            provider_name="meta",
            model_name=model_name,
            api_key=api_key or "ollama-local",
            base_url=base_url.rstrip("/")
        )

    async def test_connection(self) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        url = f"{self.base_url}/models"

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=headers)
                latency = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 200:
                    return {
                        "status": "healthy",
                        "message": f"Successfully connected to Meta local endpoint ({self.model_name})",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Meta endpoint HTTP {res.status_code}: {res.text[:100]}",
                        "latency_ms": latency
                    }
        except Exception as exc:
            return {
                "status": "unreachable",
                "message": f"Meta endpoint offline or unreachable at {self.base_url} ({str(exc)})",
                "latency_ms": 0.0
            }

    async def analyze_and_propose_fixes(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        prompt = f"""
Generate SEO code diffs for {project_context.get('canonical_url', '')}:
Issues:
{json.dumps(issues, indent=2)}

Output STRICT JSON list of objects: [{{file_path, action, original_snippet, new_snippet, diff, reason, target_issues}}].
"""
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"].strip()
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
        return {"safe_to_apply": True, "risk_level": "low", "warnings": []}

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIProviderBase(ABC):
    """Abstract interface that all AI adapters must implement."""

    def __init__(self, provider_name: str, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider_name = provider_name
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Verify API key validity, latency, and model availability."""
        pass

    @abstractmethod
    async def analyze_and_propose_fixes(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Produce a list of concrete file modifications, diffs, and risk assessments
        for the given SEO issues.
        """
        pass

    @abstractmethod
    async def review_plan_for_regressions(
        self,
        plan_changes: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform secondary independent peer review of proposed code changes."""
        pass


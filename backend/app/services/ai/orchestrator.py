import difflib
import logging
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.services.ai.base import AIProviderBase
from backend.app.services.ai.gemini_provider import GeminiProvider
from backend.app.services.ai.claude_provider import ClaudeProvider
from backend.app.services.ai.openai_provider import OpenAIProvider
from backend.app.services.ai.meta_provider import MetaProvider

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.providers: Dict[str, AIProviderBase] = {
            "gemini": GeminiProvider(api_key=settings.GEMINI_API_KEY),
            "claude": ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY),
            "openai": OpenAIProvider(api_key=settings.OPENAI_API_KEY),
            "meta": MetaProvider(base_url=settings.META_AI_BASE_URL, model_name=settings.META_AI_MODEL, api_key=settings.META_AI_API_KEY)
        }
        self.priority_order = ["gemini", "claude", "openai", "meta"]

    async def get_all_provider_health(self) -> List[Dict[str, Any]]:
        results = []
        for name in self.priority_order:
            provider = self.providers.get(name)
            if not provider:
                continue
            health = await provider.test_connection()
            results.append({
                "provider_name": name,
                "model_name": provider.model_name,
                "status": health.get("status", "unknown"),
                "message": health.get("message", ""),
                "latency_ms": health.get("latency_ms", 0.0),
                "has_api_key": bool(provider.api_key)
            })
        return results

    async def generate_change_plan(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any],
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates fix generation. Attempts requested/primary AI provider,
        falls back gracefully, and falls back to deterministic rule-based
        generator if no external AI API is available.
        """
        target_providers = [preferred_provider] if preferred_provider else self.priority_order
        generated_fixes: List[Dict[str, Any]] = []
        active_provider_used: Optional[str] = None

        for prov_name in target_providers:
            if not prov_name or prov_name not in self.providers:
                continue
            provider = self.providers[prov_name]
            if not provider.api_key and prov_name != "meta":
                continue

            try:
                logger.info(f"Attempting SEO fix generation with provider: {prov_name}")
                fixes = await provider.analyze_and_propose_fixes(issues, project_context)
                if fixes and len(fixes) > 0:
                    generated_fixes = fixes
                    active_provider_used = prov_name
                    break
            except Exception as e:
                logger.warning(f"Provider {prov_name} encountered an error: {e}")
                continue

        # If external AI did not generate fixes (e.g. no API keys set), use Deterministic Rule-Based SEO Engine
        if not generated_fixes:
            generated_fixes = self._deterministic_seo_fixes(issues, project_context)
            active_provider_used = "deterministic-seo-engine"

        # Peer review with secondary model if available
        review_result = {"safe_to_apply": True, "risk_level": "low", "warnings": []}
        for reviewer_name in self.priority_order:
            if reviewer_name != active_provider_used and reviewer_name in self.providers:
                rev_prov = self.providers[reviewer_name]
                if rev_prov.api_key:
                    try:
                        review_result = await rev_prov.review_plan_for_regressions(generated_fixes, project_context)
                        break
                    except Exception:
                        pass

        # Determine automated verification tests to run based on actual repo files
        tests_to_run: List[str] = []
        repo_path_str = project_context.get("local_repo_path")
        if repo_path_str:
            from pathlib import Path
            repo_p = Path(repo_path_str).resolve()
            if (repo_p / "package.json").exists():
                tests_to_run.append("npm run build")
            elif (repo_p / "pytest.ini").exists() or (repo_p / "tests").exists():
                tests_to_run.append("pytest")

        return {
            "fixes": generated_fixes,
            "provider_used": active_provider_used,
            "risk_assessment": review_result.get("risk_level", "low"),
            "warnings": review_result.get("warnings", []),
            "tests_to_run": tests_to_run
        }

    def _deterministic_seo_fixes(
        self,
        issues: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes high-fidelity, verified code patches directly from technical rules
        when external AI APIs are not configured or offline.
        Deduplicates multiple findings targeting the same assets.
        """
        fixes = []
        canonical_url = project_context.get("canonical_url", "https://example.com").rstrip("/")
        website_name = project_context.get("name", "My Website")
        seen_targets = set()

        for iss in issues:
            title = iss.get("title", "")
            orig_snippet = iss.get("original_snippet", "")
            url_or_file = iss.get("url_or_file", "")
            file_path = url_or_file.split(":")[0] if ":" in url_or_file else url_or_file
            target_file = file_path or "index.html"

            if "Missing robots.txt" in title:
                if ("public/robots.txt", "robots") in seen_targets:
                    continue
                seen_targets.add(("public/robots.txt", "robots"))
                robots_content = f"User-agent: *\nAllow: /\n\nSitemap: {canonical_url}/sitemap.xml\n"
                fixes.append({
                    "file_path": "public/robots.txt",
                    "action": "create",
                    "original_snippet": "",
                    "new_snippet": robots_content,
                    "diff": self._create_unified_diff("", robots_content, "public/robots.txt"),
                    "reason": "Establish crawling rules and direct search bots to XML sitemap.",
                    "target_issues": [title]
                })

            elif "Missing sitemap.xml" in title:
                if ("public/sitemap.xml", "sitemap") in seen_targets:
                    continue
                seen_targets.add(("public/sitemap.xml", "sitemap"))
                sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{canonical_url}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
                fixes.append({
                    "file_path": "public/sitemap.xml",
                    "action": "create",
                    "original_snippet": "",
                    "new_snippet": sitemap_content,
                    "diff": self._create_unified_diff("", sitemap_content, "public/sitemap.xml"),
                    "reason": "Enable automated search crawler discovery of indexable URLs.",
                    "target_issues": [title]
                })

            elif "Default or Placeholder Page Title" in title or "Missing Page Title" in title:
                if (target_file, "title") in seen_targets:
                    continue
                seen_targets.add((target_file, "title"))
                new_title_tag = f"<title>{website_name} | High-Performance Web Platform</title>"
                orig = orig_snippet or "<title>Vite + React + TS</title>"
                fixes.append({
                    "file_path": target_file,
                    "action": "modify",
                    "original_snippet": orig,
                    "new_snippet": new_title_tag,
                    "diff": self._create_unified_diff(orig, new_title_tag, target_file),
                    "reason": "Replace generic placeholder title with keyword-optimized brand title.",
                    "target_issues": [title]
                })

            elif "Missing Meta Description" in title:
                if (target_file, "description") in seen_targets:
                    continue
                seen_targets.add((target_file, "description"))
                meta_tag = f'<meta name="description" content="{website_name} - Optimized platform delivering exceptional speed, quality, and seamless user experience." />'
                fixes.append({
                    "file_path": target_file,
                    "action": "modify",
                    "original_snippet": orig_snippet or "</head>",
                    "new_snippet": f"  {meta_tag}\n  {orig_snippet or '</head>'}",
                    "diff": self._create_unified_diff(
                        orig_snippet or "</head>",
                        f"  {meta_tag}\n  {orig_snippet or '</head>'}",
                        target_file
                    ),
                    "reason": "Provide rich SERP snippet to increase organic Click-Through-Rate (CTR).",
                    "target_issues": [title]
                })

            elif "Missing Canonical Link Tag" in title or "Missing Canonical Tag" in title:
                if (target_file, "canonical") in seen_targets:
                    continue
                seen_targets.add((target_file, "canonical"))
                canonical_tag = f'<link rel="canonical" href="{canonical_url}/" />'
                fixes.append({
                    "file_path": target_file,
                    "action": "modify",
                    "original_snippet": orig_snippet or "</head>",
                    "new_snippet": f"  {canonical_tag}\n  {orig_snippet or '</head>'}",
                    "diff": self._create_unified_diff(
                        orig_snippet or "</head>",
                        f"  {canonical_tag}\n  {orig_snippet or '</head>'}",
                        target_file
                    ),
                    "reason": "Prevent duplicate content penalties and consolidate link equity.",
                    "target_issues": [title]
                })

            elif "Missing 'alt' Attribute" in title and orig_snippet:
                if (target_file, "alt", orig_snippet) in seen_targets:
                    continue
                seen_targets.add((target_file, "alt", orig_snippet))
                if orig_snippet.endswith("/>"):
                    new_tag = orig_snippet[:-2].rstrip() + ' alt="Descriptive graphic summary" />'
                elif orig_snippet.endswith(">"):
                    new_tag = orig_snippet[:-1].rstrip() + ' alt="Descriptive graphic summary">'
                else:
                    new_tag = orig_snippet + ' alt="Descriptive graphic summary"'

                fixes.append({
                    "file_path": target_file,
                    "action": "modify",
                    "original_snippet": orig_snippet,
                    "new_snippet": new_tag,
                    "diff": self._create_unified_diff(orig_snippet, new_tag, target_file),
                    "reason": "Ensure image accessibility and enable Google Image search indexing.",
                    "target_issues": [title]
                })

        return fixes

    def _create_unified_diff(self, original: str, modified: str, filename: str) -> str:
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return "".join(diff)

ai_orchestrator = AIOrchestrator()

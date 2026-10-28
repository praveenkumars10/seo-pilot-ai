import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class CodeAnalysisIssue:
    def __init__(
        self,
        category: str,
        severity: str,
        title: str,
        file_path: str,
        line_number: Optional[int],
        evidence: str,
        original_snippet: str,
        root_cause_hypothesis: str,
        recommended_fix: str
    ):
        self.category = category
        self.severity = severity
        self.title = title
        self.file_path = file_path
        self.line_number = line_number
        self.evidence = evidence
        self.original_snippet = original_snippet
        self.root_cause_hypothesis = root_cause_hypothesis
        self.recommended_fix = recommended_fix

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "url_or_file": f"{self.file_path}:{self.line_number}" if self.line_number else self.file_path,
            "evidence": self.evidence,
            "root_cause_hypothesis": self.root_cause_hypothesis,
            "recommended_fix": self.recommended_fix,
            "original_snippet": self.original_snippet,
            "confidence": 0.95
        }

class LocalCodeAnalyzerService:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.supported_extensions = {".html", ".htm", ".jsx", ".tsx", ".vue", ".astro", ".php"}
        self.ignore_dirs = {
            "node_modules", ".git", ".next", "dist", "build", "venv", ".venv",
            "__pycache__", ".vscode", ".idea", "vendor"
        }

    def analyze_repository(self) -> List[Dict[str, Any]]:
        """Scan repository files for technical SEO issues with exact line citations."""
        if not self.repo_path.exists() or not self.repo_path.is_dir():
            return []

        issues: List[CodeAnalysisIssue] = []

        # 1. Check for public/robots.txt and public/sitemap.xml
        self._check_public_assets(issues)

        # 2. Traverse source files
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith(".")]

            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in self.supported_extensions:
                    full_file_path = Path(root) / file
                    rel_path = str(full_file_path.relative_to(self.repo_path)).replace("\\", "/")
                    self._analyze_file(full_file_path, rel_path, issues)

        return [iss.to_dict() for iss in issues]

    def _check_public_assets(self, issues: List[CodeAnalysisIssue]):
        public_dir = self.repo_path / "public"
        robots_paths = [
            self.repo_path / "public" / "robots.txt",
            self.repo_path / "robots.txt"
        ]
        sitemap_paths = [
            self.repo_path / "public" / "sitemap.xml",
            self.repo_path / "sitemap.xml"
        ]

        if not any(p.exists() for p in robots_paths):
            issues.append(CodeAnalysisIssue(
                category="technical",
                severity="high",
                title="Missing robots.txt in Project Webroot",
                file_path="public/robots.txt",
                line_number=None,
                evidence="No robots.txt found in public/ or root folder.",
                original_snippet="",
                root_cause_hypothesis="robots.txt has not been created or configured in the project source.",
                recommended_fix="Create public/robots.txt specifying crawler directives and Sitemap URL."
            ))

        if not any(p.exists() for p in sitemap_paths):
            issues.append(CodeAnalysisIssue(
                category="indexing",
                severity="high",
                title="Missing sitemap.xml in Project Webroot",
                file_path="public/sitemap.xml",
                line_number=None,
                evidence="No sitemap.xml found in public/ or root folder.",
                original_snippet="",
                root_cause_hypothesis="sitemap.xml file not generated or placed in public assets.",
                recommended_fix="Create public/sitemap.xml or setup dynamic sitemap generation."
            ))

    def _analyze_file(self, full_path: Path, rel_path: str, issues: List[CodeAnalysisIssue]):
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return

        content = "".join(lines)

        # 1. Missing or empty title in HTML templates / index.html
        if full_path.name in ["index.html", "layout.tsx", "layout.jsx", "App.tsx", "_document.tsx"]:
            if "<title>" in content:
                title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL | re.IGNORECASE)
                if title_match:
                    title_text = title_match.group(1).strip()
                    if not title_text or title_text.lower() in ["vite + react + ts", "react app", "vite app", "document"]:
                        line_no = self._find_line_number(lines, "<title>")
                        issues.append(CodeAnalysisIssue(
                            category="meta",
                            severity="critical",
                            title="Default or Placeholder Page Title in Code",
                            file_path=rel_path,
                            line_number=line_no,
                            evidence=f"Placeholder title detected: '{title_text}'",
                            original_snippet=title_match.group(0),
                            root_cause_hypothesis="Default starter template title was not replaced with branded SEO title.",
                            recommended_fix="Update <title> with a brand name and descriptive keywords."
                        ))

            # 2. Check meta description
            if not re.search(r'<meta\s+name=["\']description["\']', content, re.IGNORECASE):
                head_line = self._find_line_number(lines, "</head>") or self._find_line_number(lines, "<head>")
                issues.append(CodeAnalysisIssue(
                    category="meta",
                    severity="high",
                    title="Missing Meta Description Tag in Head",
                    file_path=rel_path,
                    line_number=head_line,
                    evidence="No <meta name='description' content='...'> found in head section.",
                    original_snippet=lines[head_line - 1].strip() if head_line and head_line <= len(lines) else "",
                    root_cause_hypothesis="Document head is missing primary meta description tag.",
                    recommended_fix="Add <meta name='description' content='Comprehensive website description.' />."
                ))

            # 3. Check canonical tag
            if not re.search(r'<link\s+rel=["\']canonical["\']', content, re.IGNORECASE):
                head_line = self._find_line_number(lines, "</head>") or self._find_line_number(lines, "<head>")
                issues.append(CodeAnalysisIssue(
                    category="indexing",
                    severity="medium",
                    title="Missing Canonical Link Tag in Head",
                    file_path=rel_path,
                    line_number=head_line,
                    evidence="No <link rel='canonical' href='...'> found in template head.",
                    original_snippet=lines[head_line - 1].strip() if head_line and head_line <= len(lines) else "",
                    root_cause_hypothesis="Template does not declare a canonical self-referencing URL.",
                    recommended_fix="Add <link rel='canonical' href='https://yourdomain.com/' />."
                ))

        # 4. Scan image tags for missing alt attribute across all component files
        for i, line in enumerate(lines, start=1):
            # Check img tags
            img_matches = re.finditer(r'<img\s+([^>]*?)>', line, re.IGNORECASE)
            for m in img_matches:
                img_tag_str = m.group(0)
                # Check if alt attribute exists
                if not re.search(r'\balt=["\']', img_tag_str, re.IGNORECASE):
                    issues.append(CodeAnalysisIssue(
                        category="content",
                        severity="medium",
                        title="Missing 'alt' Attribute on <img> Element",
                        file_path=rel_path,
                        line_number=i,
                        evidence=f"Line {i}: {img_tag_str}",
                        original_snippet=img_tag_str,
                        root_cause_hypothesis="Image markup lacks required accessibility and SEO alt attribute.",
                        recommended_fix=f"Add descriptive alt text: {img_tag_str[:-1]} alt=\"Descriptive image summary\">"
                    ))

            # Check for Next.js Image component missing alt
            next_img_matches = re.finditer(r'<Image\s+([^>]*?)>', line)
            for m in next_img_matches:
                tag_str = m.group(0)
                if not re.search(r'\balt=["\']', tag_str):
                    issues.append(CodeAnalysisIssue(
                        category="content",
                        severity="medium",
                        title="Missing 'alt' on Next.js <Image> Component",
                        file_path=rel_path,
                        line_number=i,
                        evidence=f"Line {i}: {tag_str}",
                        original_snippet=tag_str,
                        root_cause_hypothesis="Next.js Image component rendered without required alt prop.",
                        recommended_fix=f"Add alt prop: {tag_str[:-1]} alt=\"Image description\">"
                    ))

    def _find_line_number(self, lines: List[str], substring: str) -> Optional[int]:
        for idx, line in enumerate(lines, start=1):
            if substring.lower() in line.lower():
                return idx
        return None


import pytest
from pathlib import Path
from backend.app.services.code_analyzer import LocalCodeAnalyzerService

def test_code_analyzer_detects_missing_assets_and_alt(tmp_path):
    # Setup temporary mock repository
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    component_file = src_dir / "Header.tsx"
    component_file.write_text("""
    export function Header() {
      return (
        <header>
          <img src="/avatar.jpg" />
        </header>
      );
    }
    """, encoding="utf-8")

    index_html = tmp_path / "index.html"
    index_html.write_text("""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Vite + React + TS</title>
      </head>
      <body>
        <div id="root"></div>
      </body>
    </html>
    """, encoding="utf-8")

    analyzer = LocalCodeAnalyzerService(repo_path=str(tmp_path))
    issues = analyzer.analyze_repository()

    issue_titles = [i["title"] for i in issues]
    assert "Missing robots.txt in Project Webroot" in issue_titles
    assert "Missing sitemap.xml in Project Webroot" in issue_titles
    assert "Default or Placeholder Page Title in Code" in issue_titles
    assert "Missing Meta Description Tag in Head" in issue_titles
    assert any("Missing 'alt' Attribute" in t for t in issue_titles)


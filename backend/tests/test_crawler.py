import pytest
from bs4 import BeautifulSoup
from backend.app.services.crawler import SEOCrawlerService, CrawlPageResult

def test_html_analysis_missing_title_and_h1():
    html_content = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="robots" content="noindex" />
      </head>
      <body>
        <div><img src="/logo.png" /></div>
        <p>Welcome to our page</p>
      </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    crawler = SEOCrawlerService(base_url="https://example.com")
    page_res = CrawlPageResult(url="https://example.com/")

    crawler._analyze_html_page(soup, page_res)

    issue_titles = [i["title"] for i in page_res.issues]
    assert "Missing Page Title" in issue_titles
    assert "Missing Meta Description" in issue_titles
    assert "Missing Canonical Tag" in issue_titles
    assert "Page Marked Noindex" in issue_titles
    assert "Missing H1 Heading" in issue_titles
    assert any("Images Missing Alt Attribute" in t for t in issue_titles)

def test_html_analysis_healthy_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <title>Professional Web Services | Premier Platform Solutions</title>
        <meta name="description" content="Discover premier web design and engineering solutions tailored for scaling digital operations worldwide." />
        <link rel="canonical" href="https://example.com/" />
        <meta property="og:title" content="Premier Web Platform" />
        <meta property="og:image" content="https://example.com/og.jpg" />
      </head>
      <body>
        <h1>Premier Web Platform</h1>
        <img src="/logo.png" alt="Company Brand Logo" />
      </body>
    </html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    crawler = SEOCrawlerService(base_url="https://example.com")
    page_res = CrawlPageResult(url="https://example.com/")

    crawler._analyze_html_page(soup, page_res)

    severities = [i["severity"] for i in page_res.issues]
    assert "critical" not in severities
    assert page_res.title.startswith("Professional Web Services")
    assert len(page_res.h1_tags) == 1
